# pylint: disable=R0913,R1721,R1728
"""
Module for ensuring foundedness.
"""
import itertools
import re

import networkx as nx

from ..comparison_tools import ComparisonTools
from .generate_foundedness_part_comparisons import GenerateFoundednessPartComparisons
from .generate_foundedness_part_function import GenerateFoundednessPartFunction
from .helper_part import HelperPart


class GenerateFoundednessPart:
    """
    Class for ensuring foundedness.
    """

    def __init__(
        self,
        rule_head,
        current_rule_position,
        custom_printer,
        domain_lookup_dict,
        safe_variables_rules,
        rule_variables,
        rule_comparisons,
        rule_predicate_functions,
        rule_literals_signums,
        current_rule,
        strongly_connected_components,
        ground_guess,
        unfounded_rules,
        cyclic_strategy,
        strongly_connected_components_heads,
        program_rules,
        additional_unfounded_rules,
        rule_variables_predicates,
    ):
        self.rule_head = rule_head
        self.current_rule_position = current_rule_position
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.safe_variables_rules = safe_variables_rules
        self.rule_variables = rule_variables
        self.rule_comparisons = rule_comparisons
        self.rule_literals = rule_predicate_functions
        self.rule_literals_signums = rule_literals_signums
        self.current_rule = current_rule
        self.rule_strongly_restricted_components = strongly_connected_components
        self.ground_guess = ground_guess
        self.unfounded_rules = unfounded_rules
        self.cyclic_strategy = cyclic_strategy
        self.rule_strongly_restricted_components_heads = (
            strongly_connected_components_heads
        )
        self.program_rules = program_rules
        self.rule_variables_predicates = rule_variables_predicates

        self.additional_unfounded_rules = additional_unfounded_rules

    def generate_foundedness_part(self):
        """
        Method which generates the foundedness part.
        """
        # head
        h_args_len = len(self.rule_head.arguments)
        h_args = re.sub(r"^.*?\(", "", str(self.rule_head))[:-1].split(
            ","
        )  # all arguments (incl. duplicates / terms)
        h_args_nd = list(
            dict.fromkeys(h_args)
        )  # arguments (without duplicates / incl. terms)
        h_vars = list(
            dict.fromkeys([a for a in h_args if a in self.rule_variables])
        )  # which have to be grounded per combination

        variables_not_in_head = []
        for variable in self.rule_variables:
            if variable != "_" and variable not in h_vars:
                variables_not_in_head.append(variable)
        # variables_not_in_head = [v for v in self.rule_variables if
        #       v not in h_vars]  # remaining variables not included in head atom (without facts)

        g_r = {}
        graph = self._generate_dependency_graph()

        self._generate_foundedness_head(
            self.rule_head,
            variables_not_in_head,
            graph,
            g_r,
            h_vars,
            h_args,
            h_args_len,
            h_args_nd,
        )

        if self.program_rules:
            foundedness_comparisons = GenerateFoundednessPartComparisons(
                self.rule_head,
                self.current_rule_position,
                self.printer,
                self.domain_lookup_dict,
                self.safe_variables_rules,
                self.rule_variables,
                self.rule_comparisons,
                self.rule_literals,
                self.rule_literals_signums,
                self.current_rule,
                self.rule_strongly_restricted_components,
                self.ground_guess,
                self.unfounded_rules,
                self.cyclic_strategy,
                self.rule_strongly_restricted_components_heads,
                self.program_rules,
                self.additional_unfounded_rules,
                self.rule_variables_predicates,
            )

            covered_subsets = foundedness_comparisons.generate_foundedness_comparisons(
                self.rule_head, variables_not_in_head, h_vars, h_args, graph
            )
        else:
            covered_subsets = {}

        foundedness_function = GenerateFoundednessPartFunction(
            self.rule_head,
            self.current_rule_position,
            self.printer,
            self.domain_lookup_dict,
            self.safe_variables_rules,
            self.rule_variables,
            self.rule_comparisons,
            self.rule_literals,
            self.rule_literals_signums,
            self.current_rule,
            self.rule_strongly_restricted_components,
            self.ground_guess,
            self.unfounded_rules,
            self.cyclic_strategy,
            self.rule_strongly_restricted_components_heads,
            self.program_rules,
            self.additional_unfounded_rules,
            self.rule_variables_predicates,
        )
        foundedness_function.generate_foundedness_functions(
            self.rule_head,
            variables_not_in_head,
            h_vars,
            h_args,
            graph,
            covered_subsets,
        )

    def _generate_dependency_graph(self):
        # Generate Graph for performance improvement
        graph = nx.Graph()
        for literal in self.rule_literals:
            literal_arguments_length = len(literal.arguments)
            literal_arguments = re.sub(r"^.*?\(", "", str(literal))[:-1].split(
                ","
            )  # all arguments (incl. duplicates / terms)
            if literal != self.rule_head and literal_arguments_length > 0:
                literal_variables = []
                for argument in literal_arguments:
                    if argument in self.rule_variables:
                        literal_variables.append(argument)

                literal_variables = list(set(literal_variables))

                for variable_1 in literal_variables:
                    for variable_2 in literal_variables:
                        graph.add_edge(variable_1, variable_2)

        for comparison in self.rule_comparisons:
            left = comparison.term
            assert len(comparison.guards) <= 1  # Assume top level one guard
            right = comparison.guards[0].term

            unparsed_f_args = ComparisonTools.get_arguments_from_operation(
                left
            ) + ComparisonTools.get_arguments_from_operation(right)
            f_vars = []
            for unparsed_f_arg in unparsed_f_args:
                f_arg = str(unparsed_f_arg)
                if f_arg in self.rule_variables:
                    f_vars.append(f_arg)

            for variable_1 in f_vars:
                for variable_2 in f_vars:
                    graph.add_edge(variable_1, variable_2)

        return graph

    def _generate_foundedness_head(
        self,
        head,
        variables_not_in_head,
        graph,
        reachable_head_variables_from_not_head_variable,
        head_variables,
        head_arguments,
        length_of_head_arguments,
        head_arguments_no_duplicates,
    ):
        # ---------------------------------------------
        # REM -> is for the ''remaining'' variables that do not occur in the head
        # The next part is about the introduction of the ''remaining'' variables

        for not_head_variable in variables_not_in_head:
            reachable_head_variables_from_not_head_variable[not_head_variable] = []
            for node in nx.dfs_postorder_nodes(graph, source=not_head_variable):
                if node in head_variables:
                    reachable_head_variables_from_not_head_variable[
                        not_head_variable
                    ].append(node)

            dom_list = []
            dom_list_lookup = {}
            index = 0
            for variable in reachable_head_variables_from_not_head_variable[
                not_head_variable
            ]:
                not_head_variable_values = (
                    HelperPart.get_domain_values_from_rule_variable(
                        self.current_rule_position,
                        variable,
                        self.domain_lookup_dict,
                        self.safe_variables_rules,
                        self.rule_variables_predicates,
                    )
                )
                dom_list.append(not_head_variable_values)
                dom_list_lookup[variable] = index

                index += 1

            combinations = [p for p in itertools.product(*dom_list)]

            for combination in combinations:
                if not self.ground_guess:
                    self._generate_foundedness_head_not_ground(
                        head_arguments,
                        head_variables,
                        reachable_head_variables_from_not_head_variable,
                        not_head_variable,
                        combination,
                        dom_list_lookup,
                        head,
                    )
                else:
                    self._generate_foundedness_head_ground(
                        head,
                        reachable_head_variables_from_not_head_variable,
                        head_variables,
                        head_arguments,
                        length_of_head_arguments,
                        head_arguments_no_duplicates,
                        not_head_variable,
                        dom_list_lookup,
                        combination,
                    )

    def _generate_foundedness_head_ground(
        self,
        head,
        reachable_head_variables_from_not_head_variable,
        head_variables,
        head_arguments,
        length_of_head_arguments,
        head_arguments_no_duplicates,
        not_head_variable,
        dom_list_lookup,
        combination,
    ):
        head_interpretation = self._ground_head_generate_head_string(
            head,
            reachable_head_variables_from_not_head_variable,
            head_arguments,
            length_of_head_arguments,
            not_head_variable,
            dom_list_lookup,
            combination,
        )

        remaining_head_values = []
        for variable in head_arguments_no_duplicates:
            if (
                variable
                in reachable_head_variables_from_not_head_variable[not_head_variable]
            ):
                remaining_head_values.append(combination[dom_list_lookup[variable]])

        not_head_variable_values = HelperPart.get_domain_values_from_rule_variable(
            self.current_rule_position,
            not_head_variable,
            self.domain_lookup_dict,
            self.safe_variables_rules,
            self.rule_variables_predicates,
        )

        not_variable_interpretations = []
        for value in not_head_variable_values:
            name = f"r{self.current_rule_position}f_{not_head_variable}"
            if len(remaining_head_values) > 0:
                arguments = f"({value},{','.join(remaining_head_values)})"
            else:
                arguments = f"({value})"

            not_variable_interpretations.append(f"{name}{arguments}")

        not_variable_interpretations = ";".join(not_variable_interpretations)

        not_reached_head_variables = []
        for variable in head_variables:
            if (
                variable
                not in reachable_head_variables_from_not_head_variable[
                    not_head_variable
                ]
            ):
                not_reached_head_variables.append(variable)

        if len(head_variables) == len(
            reachable_head_variables_from_not_head_variable[not_head_variable]
        ):  # removed none
            self.printer.custom_print(
                f"1{{{not_variable_interpretations}}}1 :- {head_interpretation}."
            )
        elif (
            len(reachable_head_variables_from_not_head_variable[not_head_variable]) == 0
        ):  # removed all
            self.printer.custom_print(f"1{{{not_variable_interpretations}}}1.")
        else:  # removed some
            self._ground_not_reached_variables(
                head,
                head_arguments,
                not_head_variable,
                not_variable_interpretations,
                not_reached_head_variables,
            )

    def _ground_not_reached_variables(
        self,
        head,
        head_arguments,
        not_head_variable,
        not_variable_interpretations,
        not_reached_head_variables,
    ):
        dom_list = []
        dom_list_lookup = {}

        index = 0
        for variable in not_reached_head_variables:
            values = HelperPart.get_domain_values_from_rule_variable(
                self.current_rule_position,
                not_head_variable,
                self.domain_lookup_dict,
                self.safe_variables_rules,
                self.rule_variables_predicates,
            )
            dom_list.append(values)
            dom_list_lookup[variable] = index
            index += 1

        combinations_for_not_reached_variables = [
            p for p in itertools.product(*dom_list)
        ]

        head_interpretations = []
        for combination_not_reached_variable in combinations_for_not_reached_variables:
            head_arguments_not_reached = []

            for argument in head_arguments:
                if argument in not_reached_head_variables:
                    head_arguments_not_reached.append(
                        combination_not_reached_variable[dom_list_lookup[argument]]
                    )
                else:
                    head_arguments_not_reached.append(str(argument))
                    # combination[dom_list_lookup[variable]]

            current_head_interpretation = (
                f"{head.name}({','.join(head_arguments_not_reached)})"
            )
            head_interpretations.append(current_head_interpretation)

        for head_interpretation in head_interpretations:
            self.printer.custom_print(
                f"1{{{not_variable_interpretations}}}1 :- {head_interpretation}."
            )

    def _ground_head_generate_head_string(
        self,
        head,
        reachable_head_variables_from_not_head_variable,
        head_arguments,
        length_of_head_arguments,
        not_head_variable,
        dom_list_lookup,
        combination,
    ):
        head_interpretation = f"{head.name}"
        if length_of_head_arguments > 0:
            argument_list = []
            for argument in head_arguments:
                if (
                    argument
                    in reachable_head_variables_from_not_head_variable[
                        not_head_variable
                    ]
                ):
                    argument_list.append(combination[dom_list_lookup[argument]])
                else:
                    argument_list.append(argument)
            head_interpretation += f"({','.join(argument_list)})"
        return head_interpretation

    def _generate_foundedness_head_not_ground(
        self,
        head_arguments,
        head_variables,
        graph_variable_dict,
        not_head_variable,
        combination,
        dom_list_lookup,
        head,
    ):
        head_tuple_list = []
        partly_head_tuple_list = []

        for head_argument in head_arguments:
            if (
                head_argument in head_variables
                and head_argument in graph_variable_dict[not_head_variable]
            ):
                combination_value = combination[dom_list_lookup[head_argument]]

                head_tuple_list.append(combination_value)
                partly_head_tuple_list.append(combination_value)
            elif head_argument not in head_variables:
                head_tuple_list.append(head_argument)
                partly_head_tuple_list.append(head_argument)
            else:
                head_tuple_list.append(head_argument)

        head_interpretation = f"{head.name}{self.current_rule_position}"

        if len(head_tuple_list) > 0:
            head_tuple_interpretation = ",".join(head_tuple_list)
            head_interpretation += f"({head_tuple_interpretation})"

        if str(self.current_rule_position) in self.safe_variables_rules and (
            str(not_head_variable)
            in self.safe_variables_rules[str(self.current_rule_position)]
            or str(not_head_variable) in self.rule_variables_predicates
        ):
            values = HelperPart.get_domain_values_from_rule_variable(
                self.current_rule_position,
                not_head_variable,
                self.domain_lookup_dict,
                self.safe_variables_rules,
                self.rule_variables_predicates,
            )
            for value in values:
                self.printer.custom_print(
                    f"domain_rule_{self.current_rule_position}_variable_{not_head_variable}({value})."
                )

            domain_string = (
                f"domain_rule_{self.current_rule_position}_variable_{not_head_variable}"
                + f"({not_head_variable})"
            )
        else:
            domain_string = f"dom({not_head_variable})"

        rem_tuple_list = [not_head_variable] + partly_head_tuple_list

        if len(rem_tuple_list) > 0:
            rem_tuple_list = [item for item in rem_tuple_list if len(item) > 0]
            rem_tuple_interpretation = f"({','.join(rem_tuple_list)})"
        else:
            rem_tuple_interpretation = ""

        if len(graph_variable_dict[not_head_variable]) == 0:
            self.printer.custom_print(
                "1<="
                + f"{{r{self.current_rule_position}f_{not_head_variable}{rem_tuple_interpretation}:{domain_string}}}"
                + "<=1."
            )
        else:
            self.printer.custom_print(
                "1<="
                + f"{{r{self.current_rule_position}f_{not_head_variable}{rem_tuple_interpretation}:{domain_string}}}"
                + f"<=1 :- {head_interpretation}."
            )
