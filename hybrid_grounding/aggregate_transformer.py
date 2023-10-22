# pylint: disable=C0103
"""
Transformer that transforms the aggregates according to hybrid-grounding.
"""


import clingo
from clingo.ast import Transformer

from .aggregate_strategies.aggregate_mode import AggregateMode
from .aggregate_strategies.recursive_mode import RecursiveAggregateRewriting
from .aggregate_strategies.replace_aggregate_strategy import ReplaceAggregateStrategy
from .aggregate_strategies.rewriting_aggregate_strategy import RSRewriting
from .comparison_tools import ComparisonTools
from .grounding_modes import GroundingModes


class AggregateTransformer(Transformer):
    """
    Transformer that transforms the aggregates according to hybrid-grounding.
    """

    def __init__(self, aggregate_mode, domain, grounding_mode):
        self.aggregate_mode = aggregate_mode
        self.domain = domain

        self.new_prg = []
        self.aggregate_count = 0

        self.shown_predicates = []

        self.cur_function = None

        self.cur_head = None
        self.cur_has_aggregate = False
        self.cur_aggregates = []
        self.cur_variable_dependencies = {}

        self.rule_positive_body = []

        self.in_head = False
        self.in_body = False
        self.rules = False

        self.grounding_mode = grounding_mode

    def _reset_temporary_rule_variables(self):
        self.cur_head = None
        self.cur_has_aggregate = False
        self.cur_aggregates = []
        self.cur_variable_dependencies = {}
        self.rule_positive_body = []

    def visit_Program(self, node):
        """
        Visits the program in the Clingo-AST.
        """
        if node.name == "rules":
            self.rules = True
            if self.grounding_mode != GroundingModes.REWRITE_AGGREGATES_NO_GROUND:
                self.new_prg.append(str(node))
        else:
            self.rules = False

        return node

    def visit_Minimize(self, node):
        """
        Visit minimize stm. in clingo-AST.
        """
        self.new_prg.append(f"{str(node)}")

        return node

    def visit_Function(self, node):
        """
        Visit function in clingo-AST.
        """
        self.cur_function = node

        self.visit_children(node)

        self.shown_predicates.append(f"#show {node.name}/{len(node.arguments)}.")

        self.cur_function = None

        return node

    def visit_Rule(self, node):
        """
        Visit rule in clingo-AST.
        """
        self.cur_head = node.head

        if "head" in node.child_keys:
            self.in_head = True
            old = getattr(node, "head")
            self._dispatch(old)
            # self.visit_children(node.head)
            self.in_head = False

        if "body" in node.child_keys:
            self.in_body = True
            old = getattr(node, "body")
            self._dispatch(old)
            self.in_body = False

        if not self.cur_has_aggregate or not self.rules:
            self._rule_has_no_aggregates(node)

        else:
            self._rule_has_aggregates(node)

        self._reset_temporary_rule_variables()  # MUST BE LAST
        return node

    def _rule_has_aggregates(self, node):
        head = str(node.head)
        remaining_body = []

        for body_item in node.body:
            if body_item.atom.ast_type != clingo.ast.ASTType.BodyAggregate:
                remaining_body.append(str(body_item))

        for aggregate_index in range(len(self.cur_aggregates)):
            remaining_body += self._add_aggregate_helper_rules(aggregate_index)

        remaining_body_string = ",".join(remaining_body)
        new_rule = f"{head} :- {remaining_body_string}."
        self.new_prg.append(new_rule)

    def _rule_has_no_aggregates(self, node):
        body_rep = ""

        if node.head.ast_type == clingo.ast.ASTType.Disjunction:
            new_head = "|".join([str(elem) for elem in node.head.elements])
        else:
            new_head = str(node.head)

        for body_element_index in range(len(node.body)):
            body_elem = node.body[body_element_index]
            if body_element_index < len(node.body) - 1:
                body_rep += f"{str(body_elem)},"
            else:
                body_rep += f"{str(body_elem)}"

        if len(node.body) > 0:
            self.new_prg.append(f"{new_head} :- {body_rep}.")
        else:
            self.new_prg.append(f"{new_head}.")

    def visit_Literal(self, node):
        """
        Visit literal in clingo-AST.
        """
        self.visit_children(node)

        if (
            node.atom.ast_type != clingo.ast.ASTType.BodyAggregate
            and node.sign == 0
            and not self.in_head
        ):
            self.rule_positive_body.append(node)

        return node

    def visit_BodyAggregate(self, node):
        """
        Visit body aggregate in clingo AST.
        """
        self.cur_has_aggregate = True

        aggregate_dict = {}
        aggregate_dict["left_guard"] = node.left_guard
        aggregate_dict["right_guard"] = node.right_guard

        if node.function == 0:
            function = (0, "count")
        elif node.function == 1:
            function = (1, "sum")
        elif node.function == 2:
            function = (2, "sumplus")
        elif node.function == 3:
            function = (3, "min")
        elif node.function == 4:
            function = (4, "max")
        else:
            print(node.function)
            assert False  # Not Implemented

        aggregate_dict["function"] = function

        aggregate_dict["id"] = self.aggregate_count
        self.aggregate_count += 1

        aggregate_dict["elements"] = []

        for element in node.elements:
            self.visit_BodyAggregateElement(element, aggregate_dict=aggregate_dict)

        self.cur_aggregates.append(aggregate_dict)

        return node

    def visit_BodyAggregateElement(self, node, aggregate_dict=None):
        """
        Visit body-aggregate-element in clingo AST.
        """
        if aggregate_dict:
            element_dict = {}

            term_strings = []
            for term in node.terms:
                term_strings.append(str(term))

            element_dict["terms"] = term_strings

            element_dict["condition_variables"] = []

            condition_ast_list = []
            condition_strings = []
            for condition in node.condition:
                self.for_each_aggregate_condition(
                    element_dict, condition_ast_list, condition_strings, condition
                )

            element_dict["condition"] = condition_strings
            element_dict["condition_ast"] = condition_ast_list

            aggregate_dict["elements"].append(element_dict)

        return node

    def for_each_aggregate_condition(
        self, element_dict, condition_ast_list, condition_strings, condition
    ):
        """
        For each aggregate condition the following code is executed.
        """
        condition_ast_list.append(condition)

        if (
            hasattr(condition, "atom")
            and hasattr(condition.atom, "symbol")
            and condition.atom.symbol.ast_type == clingo.ast.ASTType.Function
        ):
            self._aggregate_condition_is_function(element_dict, condition)

        elif (
            hasattr(condition, "atom")
            and condition.atom.ast_type == clingo.ast.ASTType.Comparison
        ):
            self._aggregate_condition_is_comparison(element_dict, condition)

        else:
            print(condition)
            print(condition.ast_type)
            assert False

        if self.aggregate_mode == AggregateMode.RS_PLUS:
            self._rs_plus_aggregate_condition_special_case(condition_strings, condition)

        else:
            condition_strings.append(str(condition))

    def _aggregate_condition_is_function(self, element_dict, condition):
        for argument in condition.atom.symbol.arguments:
            if argument.ast_type == clingo.ast.ASTType.Variable:
                if str(argument) not in element_dict["condition_variables"]:
                    element_dict["condition_variables"].append(str(argument))

    def _aggregate_condition_is_comparison(self, element_dict, condition):
        comparison = condition.atom

        left = comparison.term
        assert len(comparison.guards) <= 1
        right = comparison.guards[0].term

        left_arguments = ComparisonTools.get_arguments_from_operation(left)
        for argument in left_arguments:
            if argument.ast_type == clingo.ast.ASTType.Variable:
                if str(argument) not in element_dict["condition_variables"]:
                    element_dict["condition_variables"].append(str(argument))

        right_arguments = ComparisonTools.get_arguments_from_operation(right)
        for argument in right_arguments:
            if argument.ast_type == clingo.ast.ASTType.Variable:
                if str(argument) not in element_dict["condition_variables"]:
                    element_dict["condition_variables"].append(str(argument))

    def _rs_plus_aggregate_condition_special_case(self, condition_strings, condition):
        if (
            hasattr(condition, "atom")
            and hasattr(condition.atom, "symbol")
            and condition.atom.symbol.ast_type == clingo.ast.ASTType.Function
        ):
            cur_dict = {}
            cur_dict["all"] = str(condition)
            cur_dict["name"] = str(condition.atom.symbol.name)
            cur_dict["arguments"] = []

            for argument in condition.atom.symbol.arguments:
                if argument.ast_type == clingo.ast.ASTType.Variable:
                    variable_argument = {}
                    variable_argument["variable"] = str(argument)

                    cur_dict["arguments"].append(variable_argument)

                elif argument.ast_type == clingo.ast.ASTType.SymbolicTerm:
                    term_argument = {}
                    term_argument["term"] = str(argument)

                    cur_dict["arguments"].append(term_argument)

                else:
                    print(argument)
                    print(argument.ast_type)
                    print("NOT IMPLEMENTED")
                    assert False  # Not implemented

            condition_strings.append(cur_dict)
        elif (
            hasattr(condition, "atom")
            and condition.atom.ast_type == clingo.ast.ASTType.Comparison
        ):
            cur_dict = {}
            cur_dict["all"] = str(condition)
            cur_dict["comparison"] = condition.atom

            condition_strings.append(cur_dict)

        else:
            print(condition)
            print(condition.ast_type)
            assert False

    def visit_Variable(self, node):
        """
        Visit variable in clingo-ast.
        """
        if str(self.cur_function) == str(self.cur_head):
            return node

        if str(node) not in self.cur_variable_dependencies:
            self.cur_variable_dependencies[str(node)] = []

        self.cur_variable_dependencies[str(node)].append(self.cur_function)

        return node

    def _add_aggregate_helper_rules(self, aggregate_index):
        """
        Helper method for rewriting the aggregates.
        Detects which aggregate strategy should be used.
        """

        aggregate = self.cur_aggregates[aggregate_index]

        # Get all variables into a list that occur in all elements of the aggregate
        all_aggregate_variables = []
        for element in aggregate["elements"]:
            temporary_variables = element["condition_variables"]

            for variable in temporary_variables:
                if variable not in all_aggregate_variables:
                    all_aggregate_variables.append(variable)

        variables_dependencies_aggregate = []

        for variable in all_aggregate_variables:
            if variable in self.cur_variable_dependencies:
                variables_dependencies_aggregate.append(variable)

        remaining_body = []
        if self.aggregate_mode == AggregateMode.RS_STAR:
            (
                program_list,
                remaining_body_part,
                program_set,
            ) = RSRewriting.rewriting_aggregate_strategy(
                aggregate,
                variables_dependencies_aggregate,
                self.aggregate_mode,
                self.cur_variable_dependencies,
                self.domain,
                self.rule_positive_body,
            )

            self.new_prg = self.new_prg + program_list + program_set
            remaining_body = remaining_body_part

        elif self.aggregate_mode == AggregateMode.RS_PLUS:
            (
                program_list,
                remaining_body_part,
                program_set,
            ) = RSRewriting.rewriting_no_body_aggregate_strategy(
                aggregate,
                variables_dependencies_aggregate,
                self.aggregate_mode,
                self.cur_variable_dependencies,
                self.domain,
                self.rule_positive_body,
            )

            self.new_prg = self.new_prg + program_list + program_set
            remaining_body = remaining_body_part

        elif self.aggregate_mode == AggregateMode.RA:
            (
                program_list,
                remaining_body_part,
                program_set,
            ) = ReplaceAggregateStrategy.replace_aggregate_strategy(
                aggregate, variables_dependencies_aggregate, self.grounding_mode
            )

            self.new_prg = self.new_prg + program_list + program_set
            remaining_body = remaining_body_part

        elif self.aggregate_mode == AggregateMode.RS:
            (
                program_list,
                remaining_body_part,
                program_set,
            ) = RSRewriting.rewriting_aggregate_strategy(
                aggregate,
                variables_dependencies_aggregate,
                self.aggregate_mode,
                self.cur_variable_dependencies,
                self.domain,
                self.rule_positive_body,
            )

            self.new_prg = self.new_prg + program_list + program_set
            remaining_body = remaining_body_part

        elif self.aggregate_mode == AggregateMode.RECURSIVE:
            (
                program_list,
                remaining_body_part,
                program_set,
            ) = RecursiveAggregateRewriting.recursive_strategy(
                aggregate,
                variables_dependencies_aggregate,
                self.domain,
                self.rule_positive_body,
            )

            self.new_prg = self.new_prg + program_list + program_set
            remaining_body = remaining_body_part

        else:
            print(f"Aggregate mode {self.aggregate_mode} not implemented!")
            assert False

        return remaining_body
