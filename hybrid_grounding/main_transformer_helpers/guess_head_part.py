# pylint: disable=R0913,R1721
"""
Module for guessing the head part.
"""

import itertools
import re

from clingo import Function

from ..cyclic_strategy import CyclicStrategy
from .helper_part import HelperPart


class GuessHeadPart:
    """
    Class for guessing the head part.
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
        current_rule,
        strongly_connected_components,
        ground_guess,
        unfounded_rules,
        cyclic_strategy,
        predicates_strongly_connected_comps,
        scc_rule_functions_scc_lookup,
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
        self.current_rule = current_rule
        self.rule_strongly_connected_components = strongly_connected_components
        self.ground_guess = ground_guess
        self.unfounded_rules = unfounded_rules
        self.cyclic_strategy = cyclic_strategy
        self.predicates_strongly_connected_comps = predicates_strongly_connected_comps
        self.scc_rule_functions_scc_lookup = scc_rule_functions_scc_lookup
        self.rule_variables_predicates = rule_variables_predicates

    def guess_head(self):
        """
        Method for guessing the head part.
        """
        new_head_name = f"{self.rule_head.name}{self.current_rule_position}"
        new_arguments = ",".join(
            [str(argument) for argument in self.rule_head.arguments]
        )

        if len(new_arguments) > 0:
            new_head = f"{new_head_name}({new_arguments})"
        else:
            new_head = f"{new_head_name}"

        if self.ground_guess:
            self.do_ground_guess(new_head_name)
        else:
            self._non_ground_guess(new_head)

        if self.current_rule in self.scc_rule_functions_scc_lookup:
            if len(new_arguments) > 0:
                new_head_func = Function(
                    name=new_head_name,
                    arguments=[
                        Function(str(f"X{index}"))
                        for index in range(len(self.rule_head.arguments))
                    ],
                )
            else:
                new_head_func = Function(name=new_head_name)

            self.scc_rule_functions_scc_lookup[self.current_rule]["head"].append(
                new_head_func
            )

    def do_ground_guess(self, new_head_name):
        """
        Method for doing a ground guess.
        """
        body_dom_dict = {}
        if (
            self.current_rule in self.rule_strongly_connected_components
            and self.cyclic_strategy == CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES
        ):
            for predicate in self.rule_strongly_connected_components[self.current_rule]:
                for argument in [str(argument) for argument in predicate.arguments]:
                    if argument in self.rule_variables:
                        body_dom_dict[
                            argument
                        ] = HelperPart.get_domain_values_from_rule_variable(
                            self.current_rule_position,
                            argument,
                            self.domain_lookup_dict,
                            self.safe_variables_rules,
                            self.rule_variables_predicates,
                        )
                    else:
                        body_dom_dict[argument] = [argument]

        body_dom_list = []
        body_dom_list_lookup = {}

        index = 0
        for key in body_dom_dict.keys():
            body_dom_list.append(body_dom_dict[key])
            body_dom_list_lookup[key] = index
            index += 1

        body_combinations = [p for p in itertools.product(*body_dom_list)]

        for body_combination in body_combinations:
            possible_head_guesses = self._generate_grounded_head_guesses(
                new_head_name, body_dom_list_lookup, body_combination
            )

            if (
                self.current_rule in self.rule_strongly_connected_components
                and self.cyclic_strategy == CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES
            ):
                self._print_grounded_head_guess_for_shared_cycle_body_predicates(
                    body_dom_list_lookup, body_combination, possible_head_guesses
                )

            else:
                self.printer.custom_print(f"{{{';'.join(possible_head_guesses)}}}.")

    def _print_grounded_head_guess_for_shared_cycle_body_predicates(
        self, body_dom_list_lookup, body_combination, possible_head_guesses
    ):
        grounded_predicates = []

        for predicate in self.rule_strongly_connected_components[self.current_rule]:
            predicate_arguments = []

            for argument in [str(argument) for argument in predicate.arguments]:
                combination_argument_position = body_dom_list_lookup[argument]
                predicate_arguments.append(
                    body_combination[combination_argument_position]
                )

            if len(predicate_arguments) > 0:
                parsed_predicate_arguments = f"({','.join(predicate_arguments)})"
            else:
                parsed_predicate_arguments = ""

            grounded_predicates.append(f"{predicate.name}{parsed_predicate_arguments}")

        if len(grounded_predicates) > 0:
            parsed_grounded_predicates = f":- {','.join(grounded_predicates)}."
        else:
            parsed_grounded_predicates = "."

        self.printer.custom_print(
            f"{{{';'.join(possible_head_guesses)}}} {parsed_grounded_predicates}"
        )

    def _generate_grounded_head_guesses(
        self, new_head_name, body_dom_list_lookup, body_combination
    ):
        head_dom_dict = {}
        for argument in [str(argument) for argument in self.rule_head.arguments]:
            if argument in body_dom_list_lookup:
                continue

            if str(argument) in self.rule_variables:
                head_dom_dict[
                    argument
                ] = HelperPart.get_domain_values_from_rule_variable(
                    self.current_rule_position,
                    argument,
                    self.domain_lookup_dict,
                    self.safe_variables_rules,
                    self.rule_variables_predicates,
                )
            else:
                head_dom_dict[argument] = [argument]

        head_dom_list = []
        head_dom_list_lookup = {}

        index = 0
        for key in head_dom_dict.keys():
            head_dom_list.append(head_dom_dict[key])
            head_dom_list_lookup[key] = index
            index += 1

        head_combinations = [p for p in itertools.product(*head_dom_list)]

        possible_head_guesses = []
        for head_combination in head_combinations:
            current_head_guess_arguments = []

            for argument in [str(argument) for argument in self.rule_head.arguments]:
                if (
                    argument not in head_dom_list_lookup
                    and argument not in body_dom_list_lookup
                ):
                    print(
                        "FATAL in guess head, could not find argument in current combination!"
                    )
                    raise Exception

                if argument in head_dom_list_lookup:
                    combination_argument_position = head_dom_list_lookup[argument]
                    current_head_guess_arguments.append(
                        head_combination[combination_argument_position]
                    )
                else:
                    combination_argument_position = body_dom_list_lookup[argument]
                    current_head_guess_arguments.append(
                        body_combination[combination_argument_position]
                    )

            if len(current_head_guess_arguments) > 0:
                parsed_current_head_guess_arguments = (
                    f"({','.join(current_head_guess_arguments)})"
                )
            else:
                parsed_current_head_guess_arguments = ""

            possible_head_guesses.append(
                f"{new_head_name}{parsed_current_head_guess_arguments}"
            )

            self.printer.custom_print(
                f"{self.rule_head.name}{parsed_current_head_guess_arguments} :- "
                + f"{new_head_name}{parsed_current_head_guess_arguments}."
            )
        return possible_head_guesses

    def _non_ground_guess(self, new_head):
        h_args = re.sub(r"^.*?\(", "", str(self.rule_head))[:-1].split(
            ","
        )  # all arguments (incl. duplicates / terms)
        h_vars = list(
            dict.fromkeys([a for a in h_args if a in self.rule_variables])
        )  # which have to be grounded per combination

        if (
            self.current_rule in self.rule_strongly_connected_components
            and self.cyclic_strategy == CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES
        ):
            string_preds = ",".join(
                [
                    str(predicate)
                    for predicate in self.rule_strongly_connected_components[
                        self.current_rule
                    ]
                ]
            )
            cyclic_behavior_arguments = f" :- {string_preds}."
        else:
            cyclic_behavior_arguments = "."

        domains = []
        for variable in h_vars:
            domains.append(
                f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})"
            )
            values = HelperPart.get_domain_values_from_rule_variable(
                self.current_rule_position,
                variable,
                self.domain_lookup_dict,
                self.safe_variables_rules,
            )
            for value in values:
                self.printer.custom_print(
                    f"domain_rule_{self.current_rule_position}_variable_{variable}({value})."
                )

        if len(domains) > 0:
            self.printer.custom_print(
                f"{{{new_head} : {','.join(domains)}}} {cyclic_behavior_arguments}"
            )
        else:
            self.printer.custom_print(f"{{{new_head}}} {cyclic_behavior_arguments}")

        self.printer.custom_print(f"{str(self.rule_head)} :- {new_head}.")
