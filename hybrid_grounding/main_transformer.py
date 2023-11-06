# pylint: disable=C0103,R0913,R1720
"""
Transforms a program according to hybrid-grounding.
"""

import re

import clingo
from clingo import Function
from clingo.ast import Transformer

from .aggregate_transformer import AggregateMode
from .cyclic_strategy import CyclicStrategy
from .main_transformer_helpers.generate_foundedness_part import GenerateFoundednessPart
from .main_transformer_helpers.generate_satisfiability_part import (
    GenerateSatisfiabilityPart,
)
from .main_transformer_helpers.guess_head_part import GuessHeadPart


class MainTransformer(Transformer):
    """
    Transforms a program according to hybrid-grounding.
    """

    def __init__(
        self,
        terms,
        facts,
        ng_heads,
        shown_predicates,
        ground_guess,
        printer,
        domain,
        safe_variables_rules,
        aggregate_mode,
        rule_strongly_connected_components,
        cyclic_strategy,
        rule_strongly_connected_comps_heads,
        predicates_strongly_connected_comps,
        scc_rule_functions_scc_lookup,
    ):
        self.terms = terms
        self.facts = facts
        self.ng_heads = ng_heads
        self.shown_predicates = shown_predicates
        self.ground_entire_output = ground_guess
        self.printer = printer
        self.domain = domain
        self.safe_variables_rules = safe_variables_rules
        self.aggregate_mode = aggregate_mode
        self.rule_strongly_connected_components = rule_strongly_connected_components
        self.cyclic_strategy = cyclic_strategy
        self.rule_strongly_connected_components_heads = (
            rule_strongly_connected_comps_heads
        )
        self.predicates_strongly_connected_comps = predicates_strongly_connected_comps
        self.scc_rule_functions_scc_lookup = scc_rule_functions_scc_lookup

        self.rule_is_non_ground = False
        self.rule_anonymous_variables = 0
        self.rule_variables = []
        self.rule_variables_predicates = {}
        self.rule_predicate_functions = []
        self.rule_literals_signums = []
        self.rule_comparisons = []

        self.foundedness_check = {}
        self.non_ground_rules = {}
        self.g_counter = "A"

        self.program_rules = False
        self.program_count = False
        self.program_sum = False
        self.program_min = False
        self.program_max = False

        self.additional_foundedness_part = []

        self.current_rule = None
        self.current_comparison = None
        self.current_predicate = None
        self.current_predicate_variable_position = 0

        self.unfounded_rules = {}
        self.current_rule_position = 0

    def _reset_after_rule(self):
        self.rule_variables = []
        self.rule_predicate_functions = []
        self.rule_literals_signums = []
        self.rule_comparisons = []
        self.rule_anonymous_variables = 0
        self.rule_is_non_ground = False
        self.rule_variables_predicates = {}

        self.current_predicate = None
        self.current_predicate_variable_position = 0

    def visit_Minimize(self, node):
        """
        Visit minimize-stmt. in clingo-AST.
        """
        self.printer.custom_print(f"{str(node)}")

        return node

    def visit_Rule(self, node):
        """
        Visit Rule in clingo-AST.
        """

        return_from_method = self.handle_no_rewrite_rule(node)

        if return_from_method is True:
            return node

        aggregate_program_stmt = (
            self.program_count
            or self.program_sum
            or self.program_min
            or self.program_max
        )

        if (
            aggregate_program_stmt
            and self.aggregate_mode == AggregateMode.RA
            and self.program_rules
        ):
            self._output_node_format_conform(node)

            return node

        self.current_rule = node

        self.visit_children(node)

        if self.rule_is_non_ground:
            return_value = self.handle_non_ground_rule(node)
            if return_value is False:
                return node
        else:
            self.handle_ground_rule(node)

        self.current_rule_position += 1
        self._reset_after_rule()

        return node

    def visit_Literal(self, node):
        """
        Visits a clingo-AST literal.
        """
        if str(node) != "#false":
            if (
                node.atom.ast_type is clingo.ast.ASTType.SymbolicAtom
            ):  # comparisons are reversed by parsing, therefore always using not is sufficient
                if str(node).startswith("not"):
                    self.rule_literals_signums.append(True)
                else:
                    self.rule_literals_signums.append(False)

                # self.rule_literals_signums.append(str(node).startswith("not "))
        self.visit_children(node)
        return node

    def visit_Function(self, node):
        """
        Visits a clingo-AST function.
        """
        if not self.current_comparison:
            self.current_predicate = node
            if node.name in self.shown_predicates:
                self.shown_predicates[node.name].add(len(node.arguments))
            else:
                self.shown_predicates[node.name] = {len(node.arguments)}

            node = node.update(**self.visit_children(node))
            self.rule_predicate_functions.append(node)
            self.current_predicate = None
            self.current_predicate_variable_position = 0

        return node

    def visit_Variable(self, node):
        """
        Visits a clingo-AST variable.
        """
        self.rule_is_non_ground = True

        if str(node) == "_":
            to_add_variable = f"Anon{self.rule_anonymous_variables}"
            node = node.update(name=to_add_variable)
            self.rule_anonymous_variables += 1
        else:
            to_add_variable = str(node)

        if (str(node) not in self.rule_variables) and str(node) not in self.terms:
            self.rule_variables.append(to_add_variable)

        if self.current_predicate is not None:
            if to_add_variable not in self.rule_variables_predicates:
                self.rule_variables_predicates[to_add_variable] = []
            self.rule_variables_predicates[to_add_variable].append(
                (self.current_predicate, self.current_predicate_variable_position)
            )

            self.current_predicate_variable_position += 1

        return node

    def visit_SymbolicTerm(self, node):
        """
        Visits a clingo-AST symbolic term (constant)
        """
        if self.current_predicate is not None:
            self.current_predicate_variable_position += 1

        return node

    def visit_Program(self, node):
        """
        Visits a clingo-AST program stmt. (important for distinction for aggregates)
        """
        keyword_dict = {}
        keyword_dict["rules"] = "rules"
        keyword_dict["max"] = "max"
        keyword_dict["min"] = "min"
        keyword_dict["count"] = "count"
        keyword_dict["sum"] = "sum"

        self.program_rules = False
        self.program_count = False
        self.program_sum = False
        self.program_min = False
        self.program_max = False

        if str(node.name) in keyword_dict:
            self.program_rules = True

        if str(node.name) == "count":
            self.program_count = True

        if str(node.name) == "sum":
            self.program_sum = True

        if str(node.name) == "min":
            self.program_min = True

        if str(node.name) == "max":
            self.program_max = True

        return node

    def visit_Comparison(self, node):
        """
        Visits a clinto-AST comparison.
        Left and right site of a comparison only supports a subset of possibilities,
        i.e., Variables, Constants, Binary-Operations, Unary-Operations and functions.
        """

        supported_types = [
            clingo.ast.ASTType.Variable,
            clingo.ast.ASTType.SymbolicTerm,
            clingo.ast.ASTType.BinaryOperation,
            clingo.ast.ASTType.UnaryOperation,
            clingo.ast.ASTType.Function,
        ]

        if len(node.guards) >= 2:
            assert False  # Not implemented

        left = node.term
        right = node.guards[0].term

        assert left.ast_type in supported_types
        assert right.ast_type in supported_types

        self.rule_comparisons.append(node)

        self.current_comparison = node

        self.visit_children(node)

        self.current_comparison = None

        return node

    def _generate_combination_information(self, h_args, f_vars_needed, c, head):
        interpretation = []  # interpretation-list
        interpretation_incomplete = []  # uncomplete; without removed vars
        nnv = []  # not needed vars
        combs_covered = (
            []
        )  # combinations covered with the (reduced combinations); len=1 when no variable is removed

        if h_args == [""]:  # catch head/0
            return (
                interpretation,
                interpretation_incomplete,
                [[""]],
                [
                    str(h_args.index(v))
                    for v in h_args
                    if v in f_vars_needed or v in self.terms
                ],
            )

        for _, v in enumerate(h_args):
            if v not in f_vars_needed and v not in self.terms:
                nnv.append(v)
            else:
                interpretation_incomplete.append(
                    c[f_vars_needed.index(v)] if v in f_vars_needed else v
                )
            interpretation.append(
                c[f_vars_needed.index(v)] if v in f_vars_needed else v
            )

        head_interpretation = ",".join(interpretation)  # can include vars

        if (
            head.name in self.facts
            and len(h_args) in self.facts[head.name]
            and head_interpretation in self.facts[head.name][len(h_args)]
        ):
            # no foundation check for this combination, its a fact!
            return None, None, None, None
        combs_covered.append(interpretation)

        index_vars = [
            str(h_args.index(v))
            for v in h_args
            if v in f_vars_needed or v in self.terms
        ]

        return interpretation, interpretation_incomplete, combs_covered, index_vars

    def _add_to_foundedness_check(self, pred, arity, combinations, rule, indices):
        indices = tuple(indices)

        for c in combinations:
            c = tuple(c)
            if pred not in self.foundedness_check:
                self.foundedness_check[pred] = {}
                self.foundedness_check[pred][arity] = {}
                self.foundedness_check[pred][arity][c] = {}
                self.foundedness_check[pred][arity][c][rule] = {indices}
            elif arity not in self.foundedness_check[pred]:
                self.foundedness_check[pred][arity] = {}
                self.foundedness_check[pred][arity][c] = {}
                self.foundedness_check[pred][arity][c][rule] = {indices}
            elif c not in self.foundedness_check[pred][arity]:
                self.foundedness_check[pred][arity][c] = {}
                self.foundedness_check[pred][arity][c][rule] = {indices}
            elif rule not in self.foundedness_check[pred][arity][c]:
                self.foundedness_check[pred][arity][c][rule] = {indices}
            else:
                self.foundedness_check[pred][arity][c][rule].add(indices)

    def _output_node_format_conform(self, rule):
        """
        Custom print rule according to universal format,
        i.e. replacing certain parts of the head/body (e.g. certain ';' by ',' or '#false :- [...]' by ':- [...]').
        """
        if str(rule.head) == "#false":
            self.printer.custom_print(f":- {', '.join(str(n) for n in rule.body)}.")
        else:
            body_string = f"{', '.join([str(b) for b in rule.body])}"

            if rule.head.ast_type == clingo.ast.ASTType.Aggregate:
                head_string = f"{str(rule.head)}"
            elif rule.head.ast_type == clingo.ast.ASTType.Disjunction:
                head_string = "|".join([str(elem) for elem in rule.head.elements])
            else:
                head_string = f"{str(rule.head).replace(';', ',')}"

            if len(rule.body) > 0:
                self.printer.custom_print(f"{head_string} :- {body_string}.")
            else:
                self.printer.custom_print(f"{head_string}.")

    def _output_node_format_conform_level_mappings(
        self, rule, relevant_heads, relevant_bodies
    ):
        """
        Custom print rule according to universal format for level-mappings (changed-body),
        i.e. replacing certain parts of the head/body (e.g. certain ';' by ',' or '#false :- [...]' by ':- [...]').
        """
        if str(rule.head) == "#false":
            self.printer.custom_print(f":- {', '.join(str(n) for n in rule.body)}.")
        else:
            # Simple search for SCC KEY
            rule_head = rule.head.atom.symbol

            found_scc_key = self._find_scc_key(rule, rule_head)

            body_string = f"{', '.join([str(b) for b in rule.body])}"

            if rule.head.ast_type == clingo.ast.ASTType.Aggregate:
                # head_string = f"{str(rule.head)}"
                raise Exception("NOT SUPPORTED!")
            if rule.head.ast_type == clingo.ast.ASTType.Disjunction:
                # head_string = "|".join([str(elem) for elem in rule.head.elements])
                raise Exception("NOT SUPPORTED!")

            head_string = f"{str(rule.head).replace(';', ',')}"

            if self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING:
                new_head_name = f"{rule_head.name}{self.current_rule_position}"
                # new_head_name = f"{rule_head.name}'"
            elif self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING_AAAI:
                new_head_name = f"{rule_head.name}"

            new_arguments = ",".join(
                [str(argument) for argument in rule_head.arguments]
            )
            if len(new_arguments) > 0:
                new_head_string = f"{new_head_name}({new_arguments})"
            else:
                new_head_string = f"{new_head_name}"

            if self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING:
                new_head_func = Function(
                    name=new_head_name,
                    arguments=[Function(str(arg_)) for arg_ in rule_head.arguments],
                )
                self.predicates_strongly_connected_comps[found_scc_key].append(
                    new_head_func
                )

                if rule in self.scc_rule_functions_scc_lookup:
                    self.scc_rule_functions_scc_lookup[rule]["head"].append(
                        new_head_func
                    )

            self._handle_level_mapping_strategies(
                rule,
                relevant_heads,
                relevant_bodies,
                body_string,
                head_string,
                new_head_string,
            )

            # Add satisfiability check for both methods
            self.printer.custom_print(f":- {body_string}, not {head_string}.")

    def _handle_level_mapping_strategies(
        self,
        rule,
        relevant_heads,
        relevant_bodies,
        body_string,
        head_string,
        new_head_string,
    ):
        if self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING:
            if len(rule.body) > 0:
                self.printer.custom_print(
                    f"0 <= {{{new_head_string}}} <= 1 :- {body_string}."
                )
            else:
                self.printer.custom_print(f"{new_head_string}.")

            self.printer.custom_print(f"{head_string} :- {new_head_string}.")
        elif self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING_AAAI:
            precs = []
            for relevant_head in relevant_heads:
                for relevant_body in relevant_bodies:
                    precs.append(f"prec({str(relevant_body)},{str(relevant_head)})")

            if len(precs) > 0:
                self.printer.custom_print(
                    f"{head_string} :- {body_string},{','.join(precs)}."
                )
            else:
                self.printer.custom_print(f"{head_string} :- {body_string}.")

    def _find_scc_key(self, rule, rule_head):
        found_scc_key = -1
        for scc_key in self.predicates_strongly_connected_comps.keys():
            for pred in self.predicates_strongly_connected_comps[scc_key]:
                if (
                    str(pred) == str(rule.head)
                    or str(pred) == str(rule_head.name)
                    or (str(pred.name) == str(rule_head.name))
                ):
                    found_scc_key = scc_key
                    break

        if found_scc_key < 0:
            print(str(rule.head))
            print(str(rule_head.name))
            raise Exception("COULD NOT FIND SCC KEY")
        return found_scc_key

    def handle_no_rewrite_rule(self, node):
        """
        Handle rule which shall not be rewritten.
        """

        return_from_parent_function = False

        if not self.program_rules:
            self._reset_after_rule()
            if self.cyclic_strategy not in [
                CyclicStrategy.LEVEL_MAPPING,
                CyclicStrategy.LEVEL_MAPPING_AAAI,
            ]:
                self._output_node_format_conform(node)
                self.current_rule_position += 1
                return_from_parent_function = True

            elif self.cyclic_strategy in [
                CyclicStrategy.LEVEL_MAPPING,
                CyclicStrategy.LEVEL_MAPPING_AAAI,
            ]:
                if node in self.rule_strongly_connected_components:
                    self._output_node_format_conform_level_mappings(
                        node,
                        self.rule_strongly_connected_components_heads[node],
                        self.rule_strongly_connected_components[node],
                    )
                    if self.cyclic_strategy == CyclicStrategy.LEVEL_MAPPING_AAAI:
                        self.current_rule_position += 1
                        return_from_parent_function = True
                    else:
                        return_from_parent_function = False
                else:
                    self._output_node_format_conform(node)
                    self.current_rule_position += 1
                    return_from_parent_function = True

        return return_from_parent_function

    def handle_non_ground_rule(self, node):
        """
        Handle rule which shall be rewritten and is non-ground.
        """

        if len(self.domain.keys()) == 0:
            self._reset_after_rule()
            self.current_rule_position += 1
            return False

        if self.program_rules:
            self.non_ground_rules[
                self.current_rule_position
            ] = self.current_rule_position

        if str(node.head) != "#false":
            head = self.rule_predicate_functions[0]
        else:
            head = None

        if self.program_rules:
            satisfiability_generator = GenerateSatisfiabilityPart(
                head,
                self.current_rule_position,
                self.printer,
                self.domain,
                self.safe_variables_rules,
                self.rule_variables,
                self.rule_comparisons,
                self.rule_predicate_functions,
                self.rule_literals_signums,
                self.rule_variables_predicates,
            )
            satisfiability_generator.generate_sat_part()

        if head is not None:
            # FOUND AND GUESS HEAD
            if self.program_rules:
                guess_head_generator = GuessHeadPart(
                    head,
                    self.current_rule_position,
                    self.printer,
                    self.domain,
                    self.safe_variables_rules,
                    self.rule_variables,
                    self.rule_comparisons,
                    self.rule_predicate_functions,
                    self.rule_literals_signums,
                    self.current_rule,
                    self.rule_strongly_connected_components,
                    self.ground_entire_output,
                    self.unfounded_rules,
                    self.cyclic_strategy,
                    self.predicates_strongly_connected_comps,
                    self.scc_rule_functions_scc_lookup,
                    self.rule_variables_predicates,
                )
                guess_head_generator.guess_head()

            foundedness_generator = GenerateFoundednessPart(
                head,
                self.current_rule_position,
                self.printer,
                self.domain,
                self.safe_variables_rules,
                self.rule_variables,
                self.rule_comparisons,
                self.rule_predicate_functions,
                self.rule_literals_signums,
                self.current_rule,
                self.rule_strongly_connected_components,
                self.ground_entire_output,
                self.unfounded_rules,
                self.cyclic_strategy,
                self.rule_strongly_connected_components_heads,
                self.program_rules,
                self.additional_foundedness_part,
                self.rule_variables_predicates,
            )
            foundedness_generator.generate_foundedness_part()

        return True

    def handle_ground_rule(self, node):
        """
        Handle rule which shall be rewritten and is ground.
        """

        pred = str(node.head).split("(", 1)[0]
        arguments = re.sub(r"^.*?\(", "", str(node.head))[:-1].split(",")
        arity = len(arguments)
        arguments = ",".join(arguments)

        if (
            pred in self.ng_heads
            and arity in self.ng_heads[pred]
            and not (
                pred in self.facts
                and arity in self.facts[pred]
                and arguments in self.facts[pred][arity]
            )
        ):
            for body_atom in node.body:
                if str(body_atom).startswith("not "):
                    neg = ""
                else:
                    neg = "not "
                self.printer.custom_print(
                    f"r{self.g_counter}_unfound({arguments}) :- "
                    f"{ neg + str(body_atom)}."
                )
            self._add_to_foundedness_check(
                pred, arity, [arguments.split(",")], self.g_counter, range(0, arity)
            )
            self.g_counter = chr(ord(self.g_counter) + 1)
        # print rule as it is
        self._output_node_format_conform(node)
