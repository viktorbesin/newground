# pylint: disable=C0103
"""
Preliminary transformer module/class.
Necessary for domain inference, and strongly-connected-component computation.
"""

import re

import clingo
from clingo.ast import Transformer
from networkx import DiGraph

from .comparison_tools import ComparisonTools


class TermTransformer(Transformer):
    """
    Preliminary transformer module/class.
    Necessary for domain inference, and strongly-connected-component computation.
    """

    def __init__(self, printer, no_show=False):
        self.terms = []
        self.facts = {}
        self.ng_heads = {}
        self.non_ground = False
        self.show = False
        self.shown_predicates = {}
        self.no_show = no_show
        self.printer = printer

        self.current_head = None
        self.current_head_functions = []
        self.safe_variable_rules = {}

        self.domain = {}
        self.comparison_operators_variables = {}

        self.current_comparison = None
        self.current_function = None
        self.current_function_position = 0

        self.current_rule_position = 0
        self.current_rule = None

        self.dependency_graph = DiGraph()
        self.dependency_graph_node_rule_lookup = {}
        self.dependency_graph_rule_node_lookup = {}
        self.dependency_graph_node_counter = 0
        self.current_head_predicate_names = []
        self.dependency_graph_node_rule_bodies_lookup = {}
        self.dependency_graph_node_rule_heads_lookup = {}
        self.dependency_graph_node_rules_part_lookup = {}

        self.rules_functions_lookup = {}

        self._node_signum = None
        self._head_aggregate_element = False

        self.in_body = False
        self.in_head = False

        self.in_program_rules_part = True

    def dependency_graph_update(self, predicate, rule):
        """
        Add node/predicate and relevant edges to dependency graph.
        Note that it is assumed that the head predicates are always considered first.
        """

        predicate_name = predicate.name

        if self._node_signum == 1:
            # Only looking at positive cycles (node_signum 1 -> not)
            return

        if predicate_name not in self.dependency_graph_node_rules_part_lookup:
            self.dependency_graph_node_rules_part_lookup[predicate_name] = [
                self.in_program_rules_part
            ]

        if (
            self.in_program_rules_part
            not in self.dependency_graph_node_rules_part_lookup[predicate_name]
        ):
            self.dependency_graph_node_rules_part_lookup[predicate_name].append(
                self.in_program_rules_part
            )

        if predicate_name not in self.dependency_graph_rule_node_lookup:
            self.add_predicate_name_to_dependency_graph(predicate, rule, predicate_name)
        elif predicate_name in self.dependency_graph_rule_node_lookup:
            self.update_predicate_in_dependency_graph(predicate, rule, predicate_name)

    def update_predicate_in_dependency_graph(self, predicate, rule, predicate_name):
        """
        Updates a predicate in the dependency graph.
        """

        node_counter = self.dependency_graph_rule_node_lookup[predicate_name]

        if rule not in self.dependency_graph_node_rule_lookup[node_counter]:
            self.dependency_graph_node_rule_lookup[node_counter].append(rule)

        if self.in_body:
            if node_counter not in self.dependency_graph_node_rule_bodies_lookup:
                self.dependency_graph_node_rule_bodies_lookup[node_counter] = {}

            if rule not in self.dependency_graph_node_rule_bodies_lookup[node_counter]:
                self.dependency_graph_node_rule_bodies_lookup[node_counter][rule] = []

            if (
                predicate
                not in self.dependency_graph_node_rule_bodies_lookup[node_counter][rule]
            ):
                self.dependency_graph_node_rule_bodies_lookup[node_counter][
                    rule
                ].append(predicate)

            for head_predicate_name in self.current_head_predicate_names:
                if head_predicate_name not in self.dependency_graph_rule_node_lookup:
                    self.dependency_graph_rule_node_lookup[
                        head_predicate_name
                    ] = self.dependency_graph_node_counter
                    self.dependency_graph_node_rule_lookup[
                        self.dependency_graph_node_counter
                    ] = [rule]

                    self.dependency_graph.add_node(self.dependency_graph_node_counter)
                    self.dependency_graph_node_counter += 1

                head_counter = self.dependency_graph_rule_node_lookup[
                    head_predicate_name
                ]
                if not self.dependency_graph.has_edge(node_counter, head_counter):
                    self.dependency_graph.add_edge(node_counter, head_counter)

        elif self.in_head:
            if node_counter not in self.dependency_graph_node_rule_heads_lookup:
                self.dependency_graph_node_rule_heads_lookup[node_counter] = {}

            if rule not in self.dependency_graph_node_rule_heads_lookup[node_counter]:
                self.dependency_graph_node_rule_heads_lookup[node_counter][rule] = []

            if (
                predicate
                not in self.dependency_graph_node_rule_heads_lookup[node_counter][rule]
            ):
                self.dependency_graph_node_rule_heads_lookup[node_counter][rule].append(
                    predicate
                )

    def add_predicate_name_to_dependency_graph(self, predicate, rule, predicate_name):
        """
        Adds a predicate in the dependency graph.
        """

        self.dependency_graph_rule_node_lookup[
            predicate_name
        ] = self.dependency_graph_node_counter
        self.dependency_graph_node_rule_lookup[self.dependency_graph_node_counter] = [
            rule
        ]

        self.dependency_graph.add_node(self.dependency_graph_node_counter)

        if self.in_body is True or self._head_aggregate_element is True:
            self.dependency_graph_node_rule_bodies_lookup[
                self.dependency_graph_node_counter
            ] = {}
            self.dependency_graph_node_rule_bodies_lookup[
                self.dependency_graph_node_counter
            ][rule] = [predicate]

            temp_node_counter = self.dependency_graph_node_counter

            self.dependency_graph_node_counter += 1

            for head_predicate_name in self.current_head_predicate_names:
                if head_predicate_name not in self.dependency_graph_rule_node_lookup:
                    self.dependency_graph_rule_node_lookup[
                        head_predicate_name
                    ] = self.dependency_graph_node_counter
                    self.dependency_graph_node_rule_lookup[
                        self.dependency_graph_node_counter
                    ] = [rule]

                    self.dependency_graph.add_node(self.dependency_graph_node_counter)
                    self.dependency_graph_node_counter += 1

                head_counter = self.dependency_graph_rule_node_lookup[
                    head_predicate_name
                ]
                if not self.dependency_graph.has_edge(temp_node_counter, head_counter):
                    self.dependency_graph.add_edge(temp_node_counter, head_counter)

        elif self.in_head is True:
            self.dependency_graph_node_rule_heads_lookup[
                self.dependency_graph_node_counter
            ] = {}
            self.dependency_graph_node_rule_heads_lookup[
                self.dependency_graph_node_counter
            ][rule] = [predicate]

            self.dependency_graph_node_counter += 1

    def visit_Rule(self, node):
        """
        Visits a rule in the clingo-AST.
        Ensures that children are visited.
        Assumes head is (single) literal.
        """
        self.current_head = node.head
        self.current_head_functions.append(str(node.head))

        self.current_rule = node

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

        pred = str(node.head).split("(", 1)[0]
        arguments = re.sub(r"^.*?\(", "", str(node.head))[:-1].split(",")
        arity = len(arguments)

        if self.non_ground:
            self.non_ground = False
            if str(node.head) != "#false":
                # save pred and arity for later use
                if pred not in self.ng_heads:
                    self.ng_heads[pred] = {arity}
                else:
                    self.ng_heads[pred].add(arity)
        elif len(node.body) == 0:
            # elif node.body.__len__() == 0:
            arguments = ",".join(arguments)
            if pred not in self.facts:
                self.facts[pred] = {}
                self.facts[pred][arity] = {arguments}
            elif arity not in self.facts[pred]:
                self.facts[pred][arity] = {arguments}
            else:
                self.facts[pred][arity].add(arguments)

        self.current_rule_position += 1
        self._reset_temporary_rule_variables()

        return node

    def visit_Aggregate(self, node):
        """
        Visits an aggregate in clingo AST.
        """
        if self.in_head:
            for elem in node.elements:
                self.current_head_functions.append(str(elem.literal))
                self.visit_children(elem.literal)

                self._head_aggregate_element = True
                for condition in elem.condition:
                    self.visit_Literal(condition)
                self._head_aggregate_element = False

        return node

    def _reset_temporary_rule_variables(self):
        self.current_head = None
        self.current_head_functions = []
        self.current_rule = None
        self.current_head_predicate_names = []

    def _reset_temporary_function_variables(self):
        self.current_function = None
        self.current_function_position = 0

    def _reset_temporary_comparison_variables(self):
        self.current_comparison = None

    def _add_symbolic_term_to_domain(self, identifier, position, value):
        """
        e.g. consider p(1,2).
        then one has to call this method twice:
        First Call:
            - p is the identifier
            - 0 is the position
            - 1 is the value
        Second Call:
            - p is the identifier
            - 1 is the position
            - 2 is the value
        """
        if str(identifier) not in self.domain:
            self.domain[str(identifier)] = {}

        if str(position) not in self.domain[str(identifier)]:
            self.domain[str(identifier)][str(position)] = []

        if str(value) not in self.domain[str(identifier)][str(position)]:
            self.domain[str(identifier)][str(position)].append(str(value))

        if "0_terms" not in self.domain:
            self.domain["0_terms"] = []

        if str(value) not in self.domain["0_terms"]:
            self.domain["0_terms"].append(str(value))

    def _add_safe_variable(self, identifier, position, value, safe_type):
        rule = str(self.current_rule_position)
        if rule not in self.safe_variable_rules:
            self.safe_variable_rules[rule] = {}

        if str(value) not in self.safe_variable_rules[rule]:
            self.safe_variable_rules[rule][str(value)] = []

        to_add_dict = {}
        to_add_dict["type"] = str(safe_type)
        to_add_dict["name"] = str(identifier)
        to_add_dict["position"] = str(position)
        to_add_dict["signum"] = self._node_signum

        self.safe_variable_rules[rule][str(value)].append(to_add_dict)

    def _add_comparison_to_safe_variables(self, value, operation):
        arguments = ComparisonTools.get_arguments_from_operation(operation)
        variables = []
        for argument in arguments:
            if argument.ast_type == clingo.ast.ASTType.Variable:
                variables.append(str(argument))

        rule = str(self.current_rule_position)
        if rule not in self.safe_variable_rules:
            self.safe_variable_rules[rule] = {}

        if str(value) not in self.safe_variable_rules[rule]:
            self.safe_variable_rules[rule][str(value)] = []

        to_add_dict = {}
        to_add_dict["type"] = "term"
        to_add_dict["variables"] = variables
        to_add_dict["operation"] = operation
        to_add_dict["signum"] = self._node_signum

        self.safe_variable_rules[rule][str(value)].append(to_add_dict)

    def visit_Function(self, node):
        """
        Visits a clingo-AST function (similar to non-negated literals).
        Calls relevant children (terms/variables/constants).
        Important for dependency (SCC) graph updates.
        """
        self.current_function = node

        # if not str(node.name).startswith('_dom_'):
        if node.name in self.shown_predicates:
            self.shown_predicates[node.name].add(len(node.arguments))
        else:
            self.shown_predicates[node.name] = {len(node.arguments)}

        self.visit_children(node)

        if self.in_head is True and self._head_aggregate_element is False:
            self.current_head_predicate_names.append(node.name)

        if self.current_rule is not None:
            self.dependency_graph_update(node, self.current_rule)

        if self.current_rule is not None:
            if self.current_rule not in self.rules_functions_lookup:
                self.rules_functions_lookup[self.current_rule] = {
                    "head": [],
                    "body": [],
                }

            if self.in_head is True and self._head_aggregate_element is False:
                self.rules_functions_lookup[self.current_rule]["head"].append(node)

            if self.in_body is True or self._head_aggregate_element is True:
                if self._node_signum == 0:
                    self.rules_functions_lookup[self.current_rule]["body"].append(node)

        self._reset_temporary_function_variables()

        return node

    def visit_Literal(self, node):
        """
        Visits a clingo-AST literal (negated/non-negated).
        """

        self._node_signum = node.sign
        self.visit_children(node)

        return node

    def visit_HeadAggregateElement(self, node):
        """
        Visits a clingo-AST head-aggregate.
        """

        self._head_aggregate_element = True
        self.visit_children(node)
        self._head_aggregate_element = False

        return node

    def visit_Comparison(self, node):
        """
        Visits a clingo-AST comparison.
        """

        self.current_comparison = node

        if len(node.guards) >= 2:
            assert False  # Not implemented (only e.g. A = B implemented, not A = B = C)

        left = node.term

        guard = node.guards[0]

        comparison = guard.comparison
        right = guard.term

        if comparison == int(clingo.ast.ComparisonOperator.Equal):
            if left.ast_type == clingo.ast.ASTType.Variable:
                self._add_comparison_to_safe_variables(str(left), right)

            if right.ast_type == clingo.ast.ASTType.Variable:
                self._add_comparison_to_safe_variables(str(right), left)

        self.visit_children(node)

        self._reset_temporary_comparison_variables()

        return node

    def _add_comparison(self, rule_name, variable, comparison):
        if rule_name not in self.comparison_operators_variables:
            self.comparison_operators_variables[rule_name] = {}

        if variable not in self.comparison_operators_variables[rule_name]:
            self.comparison_operators_variables[rule_name][variable] = []

        self.comparison_operators_variables[rule_name][variable].append(comparison)

    def visit_Variable(self, node):
        """
        Visits a clingo-AST variable.
        Determines safeness of variables.
        """

        if (
            self.current_function
            and str(self.current_function) not in self.current_head_functions
        ):
            self._add_safe_variable(
                self.current_function.name,
                self.current_function_position,
                str(node),
                "function",
            )
            self.current_function_position += 1

        if self.current_comparison:
            self._add_comparison(
                str(self.current_rule_position), str(node), self.current_comparison
            )

        self.non_ground = True
        return node

    def visit_Interval(self, node):
        """
        Visits an clingo-AST interval.
        Adds relevant domains.
        """
        if self.current_function:
            for value in range(int(str(node.left)), int(str(node.right)) + 1):
                self._add_symbolic_term_to_domain(
                    self.current_function.name,
                    self.current_function_position,
                    str(value),
                )

            self.current_function_position += 1

        for i in range(int(str(node.left)), int(str(node.right)) + 1):
            if str(i) not in self.terms:
                self.terms.append(str(i))

        return node

    def visit_SymbolicTerm(self, node):
        """
        Visits symbolic-term and adds relevant domains.
        """
        if self.current_function:
            self._add_symbolic_term_to_domain(
                self.current_function.name, self.current_function_position, str(node)
            )
            self.current_function_position += 1

        if str(node) not in self.terms:
            self.terms.append(str(node))

        return node

    def visit_ShowSignature(self, node):
        """
        Ensures that signature is only written to cmd-line, if no_show if false.
        """
        self.show = True
        if not self.no_show:
            self.printer.custom_print(node)
        return node

    def visit_Program(self, node):
        """
        Visits a program block in clingo AST.
        Detects relevant keywords.
        """
        keyword_dict = {}
        keyword_dict["rules"] = "rules"
        keyword_dict["max"] = "max"
        keyword_dict["min"] = "min"
        keyword_dict["count"] = "count"
        keyword_dict["sum"] = "sum"

        self.in_program_rules_part = False

        if str(node.name) in keyword_dict:
            self.in_program_rules_part = True
