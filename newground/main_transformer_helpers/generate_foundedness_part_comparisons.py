# pylint: disable=R0913,R1721,R1728
"""
Module for foundedness-comparison, i.e., it deals with the foundedness of rules like:
of e.g., ''X > 2'' in the rule ''a(X) :- b(X), X > 2.''
"""
import itertools

from ..comparison_tools import ComparisonTools
from .helper_part import HelperPart


class GenerateFoundednessPartComparisons:
    """
    Class for foundedness-comparison, i.e., it deals with the foundedness of rules like:
    of e.g., ''X > 2'' in the rule ''a(X) :- b(X), X > 2.''
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

    def generate_foundedness_comparisons(self, head, rem, h_vars, h_args, graph):
        """
        Starting method for foundedness-comparison, i.e., it deals with the foundedness of rules like:
        of e.g., ''X > 2'' in the rule ''a(X) :- b(X), X > 2.''
        """

        covered_subsets = {}
        # for every cmp operator
        for f in self.rule_comparisons:
            left = f.term
            assert len(f.guards) <= 1
            right = f.guards[0].term
            comparison_operator = f.guards[0].comparison

            symbolic_arguments = ComparisonTools.get_arguments_from_operation(
                left
            ) + ComparisonTools.get_arguments_from_operation(right)

            arguments = []
            for symbolic_argument in symbolic_arguments:
                arguments.append(str(symbolic_argument))

            f_arguments_nd = list(
                dict.fromkeys(arguments)
            )  # arguments (without duplicates / incl. terms)
            f_vars = list(
                dict.fromkeys([a for a in arguments if a in self.rule_variables])
            )  # which have to be grounded per combination

            f_rem = [
                v for v in f_vars if v in rem
            ]  # remaining vars for current function (not in head)

            f_vars_needed = HelperPart.get_vars_needed(h_vars, f_vars, f_rem, graph)
            combination_variables = f_vars_needed + f_rem

            associated_variables = {}
            dom_list = []
            index = 0
            for variable in combination_variables:
                values = HelperPart.get_domain_values_from_rule_variable(
                    self.current_rule_position,
                    variable,
                    self.domain_lookup_dict,
                    self.safe_variables_rules,
                    self.rule_variables_predicates,
                )
                dom_list.append(values)
                associated_variables[variable] = index
                index = index + 1

            combinations = [p for p in itertools.product(*dom_list)]

            for combination in combinations:
                self._generate_foundedness_comparisons_combination(
                    combination_variables,
                    combination,
                    h_vars,
                    h_args,
                    f_vars_needed,
                    associated_variables,
                    arguments,
                    left,
                    right,
                    f_vars,
                    comparison_operator,
                    f_arguments_nd,
                    rem,
                    head,
                    covered_subsets,
                )

        return covered_subsets

    def _generate_foundedness_comparisons_combination(
        self,
        combination_variables,
        combination,
        h_vars,
        h_args,
        f_vars_needed,
        associated_variables,
        arguments,
        left,
        right,
        f_vars,
        comparison_operator,
        f_arguments_nd,
        rem,
        head,
        covered_subsets,
    ):
        variable_assignments = {}

        for variable_index in range(len(combination_variables)):
            variable = combination_variables[variable_index]
            value = combination[variable_index]

            variable_assignments[variable] = value

        (
            head_combination,
            head_combination_list_2,
            unfound_atom,
            not_head_counter,
            _,
        ) = HelperPart.generate_head_atom(
            combination,
            h_vars,
            h_args,
            f_vars_needed,
            associated_variables,
            self.current_rule_position,
        )

        body_combination = {}

        self._generate_foundedness_comparisons_combination_body_combination(
            combination,
            h_vars,
            f_vars_needed,
            associated_variables,
            arguments,
            f_vars,
            not_head_counter,
            body_combination,
        )

        print_value = self._generate_foundedness_comparisons_evaluate_comparison(
            left, right, comparison_operator, variable_assignments
        )

        if print_value:
            self._generate_foundendess_comparisons_print_unfoundeness_rule(
                left,
                right,
                comparison_operator,
                f_arguments_nd,
                rem,
                covered_subsets,
                variable_assignments,
                head_combination_list_2,
                unfound_atom,
                body_combination,
            )

        self._generate_foundedness_comparisons_combination_check_unfoundeness(
            h_vars,
            h_args,
            head,
            head_combination,
            head_combination_list_2,
            unfound_atom,
        )

    def _generate_foundedness_comparisons_evaluate_comparison(
        self, left, right, comparison_operator, variable_assignments
    ):
        left_eval = ComparisonTools.evaluate_operation(left, variable_assignments)
        right_eval = ComparisonTools.evaluate_operation(right, variable_assignments)

        sint = HelperPart.ignore_exception(ValueError)(int)
        left_eval = sint(left_eval)
        right_eval = sint(right_eval)

        safe_checks = left_eval is not None and right_eval is not None
        evaluation = safe_checks and not ComparisonTools.compare_terms(
            comparison_operator, int(left_eval), int(right_eval)
        )

        print_value = not safe_checks or evaluation
        return print_value

    def _generate_foundedness_comparisons_combination_body_combination(
        self,
        combination,
        h_vars,
        f_vars_needed,
        associated_variables,
        arguments,
        f_vars,
        not_head_counter,
        body_combination,
    ):
        for f_arg in arguments:
            if f_arg in h_vars and f_arg in f_vars_needed:  # Variables in head
                associated_index = associated_variables[f_arg]
                body_combination[f_arg] = combination[associated_index]
                # body_combination[f_arg] = head_combination[f_arg]
            elif f_arg in f_vars:  # Not in head variables
                associated_index = associated_variables[f_arg]
                body_combination[f_arg] = combination[associated_index]
                # body_combination[f_arg] = (combination[not_head_counter])
                not_head_counter += 1
            else:  # Static
                body_combination[f_arg] = f_arg

    def _generate_foundendess_comparisons_print_unfoundeness_rule(
        self,
        left,
        right,
        comparison_operator,
        f_arguments_nd,
        rem,
        covered_subsets,
        variable_assignments,
        head_combination_list_2,
        unfound_atom,
        body_combination,
    ):
        left_instantiation = ComparisonTools.instantiate_operation(
            left, variable_assignments
        )
        right_instantiation = ComparisonTools.instantiate_operation(
            right, variable_assignments
        )

        ComparisonTools.comparison_handlings(
            comparison_operator, left_instantiation, right_instantiation
        )

        unfound_body_list = []

        for v in f_arguments_nd:
            if v in rem:
                body_combination_tmp = [body_combination[v]] + head_combination_list_2
                body_predicate = f"r{self.current_rule_position}f_{v}({','.join(body_combination_tmp)})"
                unfound_body_list.append(body_predicate)

        if len(unfound_body_list) > 0:
            unfound_body = f" {','.join(unfound_body_list)}"
            unfound_rule = f"{unfound_atom} :- {unfound_body}"
            unfound_rule += "."

        else:
            unfound_rule = f"{unfound_atom}"
            unfound_rule += "."

        self.printer.custom_print(unfound_rule)

        if unfound_atom not in covered_subsets:
            covered_subsets[unfound_atom] = []

        covered_subsets[unfound_atom].append(unfound_body_list)

    def _generate_foundedness_comparisons_combination_check_unfoundeness(
        self,
        h_vars,
        h_args,
        head,
        head_combination,
        head_combination_list_2,
        unfound_atom,
    ):
        dom_list_2 = []
        for arg in h_args:
            if arg in h_vars and arg not in head_combination:
                values = HelperPart.get_domain_values_from_rule_variable(
                    self.current_rule_position,
                    arg,
                    self.domain_lookup_dict,
                    self.safe_variables_rules,
                    self.rule_variables_predicates,
                )
                dom_list_2.append(values)
            elif arg in h_vars and arg in head_combination:
                dom_list_2.append([head_combination[arg]])
            else:
                dom_list_2.append([arg])

        combinations_2 = [p for p in itertools.product(*dom_list_2)]

        for combination_2 in combinations_2:
            # new_head_name = f"{head.name}{self.current_rule_position}"
            new_head_name = f"{head.name}"

            if (
                len(head_combination_list_2) > 0
                and len(list(combination_2)) > 0
                and len(("".join(combination_2)).strip()) > 0
            ):
                head_string = f"{new_head_name}({','.join(list(combination_2))})"
            else:
                head_string = f"{new_head_name}"

            # print(f"{head_string}/{unfound_atom}")
            HelperPart.add_atom_to_unfoundedness_check(
                head_string,
                unfound_atom,
                self.unfounded_rules,
                self.current_rule_position,
            )
