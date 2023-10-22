# pylint: disable=R0913,R1721
"""
Module for ensuring satisfiability.
"""
import itertools
import re

from ..comparison_tools import ComparisonTools
from .helper_part import HelperPart


class GenerateSatisfiabilityPart:
    """
    Class for ensuring satisfiability.
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
        rule_literals,
        rule_literals_signums,
        rule_variables_predicates,
    ):
        self.rule_head = rule_head
        self.current_rule_position = current_rule_position
        self.printer = custom_printer
        self.domain_lookup_dict = domain_lookup_dict
        self.safe_variables_rules = safe_variables_rules
        self.rule_variables = rule_variables
        self.rule_comparisons = rule_comparisons
        self.rule_literals = rule_literals
        self.rule_literals_signums = rule_literals_signums
        self.rule_variables_predicates = rule_variables_predicates

    def generate_sat_part(self):
        """
        Generates the SAT-part.
        """
        self._generate_sat_variable_possibilities()

        covered_subsets = self._generate_sat_comparisons()

        self._generate_sat_functions(self.rule_head, covered_subsets)

    def _generate_sat_variable_possibilities(self):
        # MOD
        # domaining per rule variable
        for variable in self.rule_variables:  # variables
            values = HelperPart.get_domain_values_from_rule_variable(
                self.current_rule_position,
                variable,
                self.domain_lookup_dict,
                self.safe_variables_rules,
                self.rule_variables_predicates,
            )

            disjunction = ""

            for value in values:
                disjunction += f"r{self.current_rule_position}_{variable}({value}) | "

            if len(disjunction) > 0:
                disjunction = disjunction[:-3] + "."
                self.printer.custom_print(disjunction)

            for value in values:
                self.printer.custom_print(
                    f"r{self.current_rule_position}_{variable}({value}) :- sat."
                )

    def _generate_sat_comparisons(self):
        covered_subsets = {}  # reduce SAT rules when compare-operators are pre-checked
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

            arguments_list = list(
                dict.fromkeys(arguments)
            )  # arguments (without duplicates / incl. terms)
            variables_list = list(
                dict.fromkeys([a for a in arguments if a in self.rule_variables])
            )  # which have to be grounded per combination
            dom_list = []
            for variable in variables_list:
                if (
                    str(self.current_rule_position) in self.safe_variables_rules
                    and variable
                    in self.safe_variables_rules[str(self.current_rule_position)]
                ):
                    domain = HelperPart.get_domain_values_from_rule_variable(
                        str(self.current_rule_position),
                        variable,
                        self.domain_lookup_dict,
                        self.safe_variables_rules,
                        self.rule_variables_predicates,
                    )

                    dom_list.append(domain)
                else:
                    dom_list.append(self.domain_lookup_dict["0_terms"])

            combinations = [p for p in itertools.product(*dom_list)]

            for c in combinations:
                variable_assignments = {}

                for variable_index in range(len(variables_list)):
                    variable = variables_list[variable_index]
                    value = c[variable_index]

                    variable_assignments[variable] = value

                interpretation_list = []
                for variable in arguments_list:
                    if variable in variables_list:
                        interpretation_list.append(
                            f"r{self.current_rule_position}_{variable}({variable_assignments[variable]})"
                        )

                left_eval = ComparisonTools.evaluate_operation(
                    left, variable_assignments
                )
                right_eval = ComparisonTools.evaluate_operation(
                    right, variable_assignments
                )

                sint = HelperPart.ignore_exception(ValueError)(int)
                left_eval = sint(left_eval)
                right_eval = sint(right_eval)

                safe_checks = left_eval is not None and right_eval is not None
                evaluation = safe_checks and not ComparisonTools.compare_terms(
                    comparison_operator, int(left_eval), int(right_eval)
                )

                if not safe_checks or evaluation:
                    left_instantiation = ComparisonTools.instantiate_operation(
                        left, variable_assignments
                    )
                    right_instantiation = ComparisonTools.instantiate_operation(
                        right, variable_assignments
                    )
                    ComparisonTools.comparison_handlings(
                        comparison_operator, left_instantiation, right_instantiation
                    )
                    interpretation = f"{','.join(interpretation_list)}"

                    sat_atom = f"sat_r{self.current_rule_position}"

                    self.printer.custom_print(f"{sat_atom} :- {interpretation}.")

                    if sat_atom not in covered_subsets:
                        covered_subsets[sat_atom] = []

                    covered_subsets[sat_atom].append(interpretation_list)

        return covered_subsets

    def _generate_sat_functions(self, head, covered_subsets):
        for current_function_symbol in self.rule_literals:
            args_len = len(current_function_symbol.arguments)
            if args_len == 0:
                signum_string = "not"
                if (
                    self.rule_literals_signums[
                        self.rule_literals.index(current_function_symbol)
                    ]
                    or current_function_symbol is head
                ):
                    signum_string = ""
                self.printer.custom_print(
                    f"sat_r{self.current_rule_position} :- {signum_string} {current_function_symbol}."
                )
                continue

            arguments = re.sub(r"^.*?\(", "", str(current_function_symbol))[:-1].split(
                ","
            )  # all arguments (incl. duplicates / terms)
            current_function_variables = list(
                dict.fromkeys([a for a in arguments if a in self.rule_variables])
            )  # which have to be grounded per combination

            variable_associations = {}
            dom_list = []
            index = 0
            for variable in current_function_variables:
                values = HelperPart.get_domain_values_from_rule_variable(
                    self.current_rule_position,
                    variable,
                    self.domain_lookup_dict,
                    self.safe_variables_rules,
                    self.rule_variables_predicates,
                )
                dom_list.append(values)
                variable_associations[variable] = index
                index += 1

            combinations = [p for p in itertools.product(*dom_list)]

            for current_combination in combinations:
                current_function_arguments_string = ""

                sat_atom = f"sat_r{self.current_rule_position}"

                (
                    sat_body_list,
                    sat_body_dict,
                    current_function_arguments_string,
                ) = self._generate_body_list(
                    arguments,
                    variable_associations,
                    current_combination,
                    current_function_arguments_string,
                )

                if (
                    self._check_covered_subsets(
                        sat_atom, covered_subsets, sat_body_dict
                    )
                    is True
                ):
                    continue

                self._print_sat_function_guess(
                    head,
                    current_function_symbol,
                    current_function_arguments_string,
                    sat_atom,
                    sat_body_list,
                )

    def _check_covered_subsets(self, sat_atom, covered_subsets, sat_body_dict):
        if sat_atom in covered_subsets:  # Check for covered subsets
            possible_subsets = covered_subsets[sat_atom]
            found = False

            for possible_subset in possible_subsets:
                temp_found = True
                for possible_subset_predicate in possible_subset:
                    if possible_subset_predicate not in sat_body_dict:
                        temp_found = False
                        break

                if temp_found is True:
                    found = True
                    break

            if found is True:
                return True

        return False

    def _print_sat_function_guess(
        self,
        head,
        current_function_symbol,
        current_function_arguments_string,
        sat_atom,
        sat_body_list,
    ):
        current_function_name = f"{current_function_symbol.name}"

        if len(current_function_arguments_string) > 0:
            current_function_string_representation = (
                f"{current_function_name}"
                + f"({current_function_arguments_string[:-1]})"
            )
        else:
            current_function_string_representation = f"{current_function_name}"

        if (
            self.rule_literals_signums[
                self.rule_literals.index(current_function_symbol)
            ]
            or current_function_symbol is head
        ):
            sat_predicate = f"{current_function_string_representation}"
        else:
            sat_predicate = f"not {current_function_string_representation}"

        if len(sat_body_list) > 0:
            body_interpretation = ",".join(sat_body_list) + ","
        else:
            body_interpretation = ""

        self.printer.custom_print(
            f"{sat_atom} :- {body_interpretation}{sat_predicate}."
        )

    def _generate_body_list(
        self,
        arguments,
        variable_associations,
        current_combination,
        current_function_arguments_string,
    ):
        sat_body_list = []
        sat_body_dict = {}
        for argument in arguments:
            if argument in self.rule_variables:
                variable_index_combination = variable_associations[argument]
                body_sat_predicate = (
                    f"r{self.current_rule_position}_{argument}"
                    + f"({current_combination[variable_index_combination]})"
                )
                sat_body_list.append(body_sat_predicate)
                sat_body_dict[body_sat_predicate] = body_sat_predicate

                current_function_arguments_string += (
                    f"{current_combination[variable_index_combination]},"
                )
            else:
                current_function_arguments_string += f"{argument},"

        sat_body_list = list(set(sat_body_list))
        return sat_body_list, sat_body_dict, current_function_arguments_string
