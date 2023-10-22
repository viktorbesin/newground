"""
Helper module for the rs-case.
"""

from .count_aggregate_helper import CountAggregateHelper
from .sum_aggregate_helper import SumAggregateHelper


class RSHelper:
    """
    Helper class for the rs-case.
    """

    @classmethod
    def add_rs_tuple_predicate_rules(
        cls,
        aggregate_dict,
        str_type,
        str_id,
        variable_dependencies,
        new_prg_part_set,
        always_add_variable_dependencies,
        rule_positive_body,
        skolem_constants,
    ):
        """
        Helper method for generating the tuple-predicates.
        """

        for element_index in range(len(aggregate_dict["elements"])):
            element = aggregate_dict["elements"][element_index]

            element_tuples = []

            for skolem_index in range(len(skolem_constants)):
                if skolem_index < len(element["terms"]):
                    element_tuples.append(element["terms"][skolem_index])
                else:
                    element_tuples.append(skolem_constants[skolem_index])

            element_dependent_variables = variable_dependencies.copy()

            for literal in always_add_variable_dependencies:
                element_dependent_variables.append(literal)

            term_string = f"{','.join(element_tuples + element_dependent_variables)}"

            if len(rule_positive_body) > 0:
                positive_body_string = (
                    ",".join([str(node) for node in rule_positive_body]) + ","
                )
            else:
                positive_body_string = ""

            body_string = (
                f"body_{str_type}_ag{str_id}({term_string}) :- "
                + f"{positive_body_string} {','.join(element['condition'])}."
            )
            new_prg_part_set.append(body_string)

    @classmethod
    def rs_count_generate_count_rule(
        cls,
        rule_head_name,
        count,
        str_type,
        str_id,
        variable_dependencies,
        always_add_variable_dependencies,
        skolem_constants,
        total_count=0,
    ):
        """
        Generates the count-rule (alldiff-rule) for the RS aggregate-mode.
        """

        rules_strings = []

        terms = []
        bodies = []

        for index in range(count):
            tuple_variables = []

            for tuple_index in range(len(skolem_constants)):
                tuple_variables.append(f"TUPLEVARIABLE_{index}_{tuple_index}")

            terms.append(tuple_variables)
            terms_string = f"{','.join(tuple_variables + variable_dependencies + always_add_variable_dependencies)}"
            bodies.append(f"body_{str_type}_ag{str_id}({terms_string})")

        helper_bodies = CountAggregateHelper.generate_all_diff_predicates(terms)
        if str_type == "sum":
            helper_bodies += SumAggregateHelper.generate_sum_up_predicates(
                terms, count, total_count
            )

        if len(always_add_variable_dependencies) == 0:
            if len(variable_dependencies) == 0:
                rule_head_ending = "(1)"
            else:
                rule_head_ending = f"({','.join(variable_dependencies)})"
        else:
            rule_head_ending = f"({','.join(variable_dependencies + always_add_variable_dependencies)})"

        rule_head = f"{rule_head_name}{rule_head_ending}"

        rules_strings.append(f"{rule_head} :- {','.join(bodies + helper_bodies)}.")

        return rules_strings

    @classmethod
    def generate_skolem_constants(cls, aggregate_dict, domain):
        """
        Helper method for generating skolem constants.
        """
        max_number_element_head = 0
        skolem_constants = []

        for element_index in range(len(aggregate_dict["elements"])):
            element = aggregate_dict["elements"][element_index]

            if len(element["terms"]) > max_number_element_head:
                max_number_element_head = len(element["terms"])

        highest_integer_value = 0
        for domain_value in domain["0_terms"]:
            if CountAggregateHelper.check_string_is_int(str(domain_value)) is True:
                if int(domain_value) > highest_integer_value:
                    highest_integer_value = int(domain_value)

        for skolem_index in range(max_number_element_head):
            skolem_constants.append(str(int(highest_integer_value + 1 + skolem_index)))

        return skolem_constants
