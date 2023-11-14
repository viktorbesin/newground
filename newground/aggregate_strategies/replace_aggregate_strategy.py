"""
Module for the RA-strategy.
"""

from ..comparison_tools import ComparisonTools
from ..grounding_modes import GroundingModes


class ReplaceAggregateStrategy:
    """
    Class for the RA-strategy.
    """

    @classmethod
    def replace_aggregate_strategy(
        cls, aggregate, variables_dependencies_aggregate, grounding_mode
    ):
        """
        Method which generates all necessary rules/etc. for the RA-strategy.
        """
        new_program_list = []
        new_program_set = []

        elements = aggregate["elements"]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"]

        element_dependent_variables_list = []

        for element_index in range(len(elements)):
            element = elements[element_index]
            element_dependent_variables = []

            for variable in element["condition_variables"]:
                if variable in variables_dependencies_aggregate:
                    element_dependent_variables.append(variable)

            element_dependent_variables_list.append(element_dependent_variables)

            terms = element["terms"]

            element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"

            terms_string = f"{','.join(terms + element_dependent_variables)}"

            element_body = f"{element_predicate_name}({terms_string})"
            body_string = f"{element_body} :- {','.join(element['condition'])}."

            new_program_list.append(body_string)

        new_elements = []

        for element_index in range(len(elements)):
            element = aggregate["elements"][element_index]

            element_dependent_variables = element_dependent_variables_list[
                element_index
            ]
            terms = element["terms"]

            element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"

            terms_string = f"{','.join(terms + element_dependent_variables)}"

            element_body = f"{element_predicate_name}({terms_string})"

            new_element = f"{','.join(element['terms'])} : {element_body}"

            new_elements.append(new_element)

        new_aggregate = ""

        if aggregate["left_guard"]:
            left_guard = aggregate["left_guard"]
            left_guard_term = str(left_guard.term)

            operator = ComparisonTools.get_comp_operator(left_guard.comparison)

            new_aggregate += f"{left_guard_term} {operator} "

        new_aggregate += f"#{str_type}{{{';'.join(new_elements)}}}"

        if aggregate["right_guard"]:
            right_guard = aggregate["right_guard"]
            right_guard_term = str(right_guard.term)

            operator = ComparisonTools.get_comp_operator(right_guard.comparison)

            new_aggregate += f" {operator} {right_guard_term}"

        if grounding_mode != GroundingModes.REWRITE_AGGREGATES_NO_GROUND:
            new_program_list.append("#program no_rules.")

        return (new_program_list, [new_aggregate], list(set(new_program_set)))
