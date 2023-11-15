# pylint: disable=R0913,R1721,R1728
"""
Module for foundedness-function, i.e., it deals with the foundedness of rules like:
of e.g., ''b(X)'' in the rule ''a(X) :- b(X), X > 2.''
"""
import itertools
import re

from ..cyclic_strategy import CyclicStrategy
from .helper_part import HelperPart


class GenerateFoundednessPartFunction:
    """
    Class for foundedness-function, i.e., it deals with the foundedness of rules like:
    of e.g., ''b(X)'' in the rule ''a(X) :- b(X), X > 2.''
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

    def generate_foundedness_functions(
        self, head, rem, h_vars, h_args, g, covered_subsets
    ):
        """
        Starting method for foundedness-function, i.e., it deals with the foundedness of rules like:
        of e.g., ''b(X)'' in the rule ''a(X) :- b(X), X > 2.''
        """

        for rule_predicate_function in self.rule_literals:
            if rule_predicate_function != head:
                len(rule_predicate_function.arguments)
                f_args = re.sub(r"^.*?\(", "", str(rule_predicate_function))[:-1].split(
                    ","
                )  # all arguments (incl. duplicates / terms)
                f_args_nd = list(
                    dict.fromkeys(f_args)
                )  # arguments (without duplicates / incl. terms)
                f_vars = list(
                    dict.fromkeys([a for a in f_args if a in self.rule_variables])
                )  # which have to be grounded per combination

                f_rem = [
                    v for v in f_vars if v in rem
                ]  # remaining vars for current function (not in head)

                f_vars_needed = HelperPart.get_vars_needed(h_vars, f_vars, f_rem, g)
                # f_vars_needed = h_vars

                associated_variables = {}
                dom_list = []
                index = 0
                for variable in f_vars_needed + f_rem:
                    values = HelperPart.get_domain_values_from_rule_variable(
                        self.current_rule_position,
                        variable,
                        self.domain_lookup_dict,
                        self.safe_variables_rules,
                        self.rule_variables_predicates,
                    )
                    dom_list.append(values)
                    associated_variables[variable] = index
                    index += 1

                combinations = [p for p in itertools.product(*dom_list)]

                for combination in combinations:
                    self._generate_foundedness_functions_combination(
                        combination,
                        h_vars,
                        h_args,
                        f_vars_needed,
                        associated_variables,
                        f_args,
                        f_vars,
                        covered_subsets,
                        f_args_nd,
                        rem,
                        rule_predicate_function,
                        head,
                    )

    def _generate_foundedness_functions_combination(
        self,
        combination,
        h_vars,
        h_args,
        f_vars_needed,
        associated_variables,
        f_args,
        f_vars,
        covered_subsets,
        f_args_nd,
        rem,
        rule_predicate_function,
        head,
    ):
        (
            head_combination,
            head_combination_list_2,
            unfound_atom,
            _,
            full_head_args,
        ) = HelperPart.generate_head_atom(
            combination,
            h_vars,
            h_args,
            f_vars_needed,
            associated_variables,
            self.current_rule_position,
        )

        # ---------
        body_combination = {}
        self._generate_foundendess_combination_body_combination(
            combination,
            h_vars,
            f_vars_needed,
            associated_variables,
            f_args,
            f_vars,
            body_combination,
        )

        (
            unfound_body_dict,
            unfound_body_list,
        ) = self._generate_foundedness_combination_unfound_body(
            f_args_nd, rem, head_combination_list_2, body_combination
        )

        if False is self._generate_foundedness_covered_subsets_check(
            covered_subsets, unfound_atom, unfound_body_dict
        ):
            return

        unfound_predicate_name = rule_predicate_function.name
        unfound_predicate = unfound_predicate_name
        if len(f_args) > 0:
            unfound_predicate += "("

            unfound_predicate_args = []
            for f_arg in f_args:
                if f_arg in body_combination:
                    unfound_predicate_args.append(body_combination[f_arg])
                else:
                    unfound_predicate_args.append(f_arg)

            unfound_predicate += f"{','.join(unfound_predicate_args)})"

        if len(unfound_body_list) > 0:
            unfound_body = f" {','.join(unfound_body_list)},"
        else:
            unfound_body = ""

        sign_adjusted_predicate = ""
        if not self.rule_literals_signums[
            self.rule_literals.index(rule_predicate_function)
        ]:  # i.e. a ''positive'' occurence (e.g. q(X) :- p(X) -> p(X) is positive)
            sign_adjusted_predicate = f"not {unfound_predicate}"
        else:  # i.e. a ''negative'' occurence (e.g. q(X) :- p(X), not p(1). -> p(1) is negative)
            sign_adjusted_predicate = f"{unfound_predicate}"

        unfound_rule = f"{unfound_atom} :-{unfound_body} {sign_adjusted_predicate}."

        if self.program_rules:
            self.printer.custom_print(unfound_rule)

        if self.cyclic_strategy in [
            CyclicStrategy.LEVEL_MAPPING,
            CyclicStrategy.LEVEL_MAPPING_AAAI,
        ]:
            self._generate_foundedness_function_combination_level_mappings(
                rule_predicate_function,
                head,
                unfound_atom,
                unfound_predicate,
                unfound_body,
                full_head_args,
                unfound_predicate_args,
            )

        self._generate_foundedness_function_combination_unfoundedness_checks(
            h_vars, h_args, head, head_combination, unfound_atom
        )

    def _generate_foundedness_covered_subsets_check(
        self, covered_subsets, unfound_atom, unfound_body_dict
    ):
        if unfound_atom in covered_subsets:
            possible_subsets = covered_subsets[unfound_atom]
            found = False

            for possible_subset in possible_subsets:
                temp_found = True
                for possible_subset_predicate in possible_subset:
                    if possible_subset_predicate not in unfound_body_dict:
                        temp_found = False
                        break

                if temp_found is True:
                    found = True
                    break

            if found is True:
                return False

        return True

    def _generate_foundedness_combination_unfound_body(
        self, f_args_nd, rem, head_combination_list_2, body_combination
    ):
        unfound_body_dict = {}
        unfound_body_list = []
        for v in f_args_nd:
            if v in rem:
                if len(("".join(head_combination_list_2)).strip()) > 0:
                    body_combination_tmp = [
                        body_combination[v]
                    ] + head_combination_list_2
                else:
                    body_combination_tmp = [body_combination[v]]
                body_predicate = f"r{self.current_rule_position}f_{v}({','.join(body_combination_tmp)})"
                unfound_body_list.append(body_predicate)
                unfound_body_dict[body_predicate] = body_predicate
        return unfound_body_dict, unfound_body_list

    def _generate_foundendess_combination_body_combination(
        self,
        combination,
        h_vars,
        f_vars_needed,
        associated_variables,
        f_args,
        f_vars,
        body_combination,
    ):
        for f_arg in f_args:
            if f_arg in h_vars and f_arg in f_vars_needed:  # Variables in head
                associated_index = associated_variables[f_arg]
                body_combination[f_arg] = combination[associated_index]
                # body_combination[f_arg] = head_combination[f_arg]
            elif f_arg in f_vars:  # Not in head variables
                if f_arg in associated_variables:
                    associated_index = associated_variables[f_arg]
                    body_combination[f_arg] = combination[associated_index]
                else:
                    body_combination[f_arg] = f_arg
            else:  # Static
                body_combination[f_arg] = f_arg

    def _generate_foundedness_function_combination_unfoundedness_checks(
        self, h_vars, h_args, head, head_combination, unfound_atom
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
            new_head_name = f"{head.name}{self.current_rule_position}"
            # new_head_name = f"{head.name}'"

            if (
                len(list(combination_2)) > 0
                and len(list(combination_2)) > 0
                and len(("".join(combination_2)).strip()) > 0
            ):
                head_string = f"{new_head_name}({','.join(list(combination_2))})"
            else:
                head_string = f"{new_head_name}"

            HelperPart.add_atom_to_unfoundedness_check(
                head_string,
                unfound_atom,
                self.unfounded_rules,
                self.current_rule_position,
            )

    def _generate_foundedness_function_combination_level_mappings(
        self,
        rule_predicate_function,
        head,
        unfound_atom,
        unfound_predicate,
        unfound_body,
        full_head_args,
        unfound_predicate_args,
    ):
        if self.current_rule in self.rule_strongly_restricted_components:
            relevant_bodies = self.rule_strongly_restricted_components[
                self.current_rule
            ]

            if rule_predicate_function in relevant_bodies:
                new_head_name = f"{head.name}{self.current_rule_position}"
                # new_head_name = f"{head.name}'"

                full_head_args = [
                    argument for argument in full_head_args if argument != ""
                ]
                if len(full_head_args) > 0:
                    head_predicate = f"{new_head_name}({','.join(full_head_args)})"
                else:
                    head_predicate = f"{new_head_name}"

                unfound_level_mapping = (
                    f"{unfound_atom} :-{unfound_body} "
                    + f"not prec({unfound_predicate},{head_predicate})."
                )
                self.printer.custom_print(unfound_level_mapping)

                if len(full_head_args) > 0:
                    original_head_predicate = f"{head.name}({','.join(full_head_args)})"
                else:
                    original_head_predicate = f"{head.name}"

                unfound_predicate_args = [
                    argument for argument in unfound_predicate_args if argument != "_"
                ]
                if len(unfound_predicate_args) > 0:
                    new_unfound_atom = (
                        f"r{self.current_rule_position}_{self.current_rule_position}_unfound"
                        + f"({','.join(unfound_predicate_args)})"
                    )
                else:
                    new_unfound_atom = f"r{self.current_rule_position}_{self.current_rule_position}_unfound_"

                unfound_level_mapping = (
                    f"{new_unfound_atom} :-"
                    + f"{unfound_body} not prec({head_predicate},{original_head_predicate})."
                )
                self.printer.custom_print(unfound_level_mapping)

                self.additional_unfounded_rules.append(
                    f":- {new_unfound_atom}, {head_predicate}."
                )
