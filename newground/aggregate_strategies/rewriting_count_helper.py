# pylint: disable=R0913
"""
Helper module for the count aggregate.
"""

from .rs_helper import RSHelper
from .rs_plus_star_helper import RSPlusStarHelper


class RewritingCountHelper:
    """
    Helper class for the count aggregate.
    """

    @classmethod
    def rs_count_generate_alldiff_rules_helper(
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
        Wrapper for the alldiff generation.
        """
        rules_strings = RSHelper.rs_count_generate_count_rule(
            rule_head_name,
            count,
            str_type,
            str_id,
            variable_dependencies,
            always_add_variable_dependencies,
            skolem_constants,
            total_count,
        )

        return rules_strings

    @classmethod
    def rs_plus_star_count_generate_alldiff_rules_helper(
        cls,
        rule_head_name,
        count,
        elements,
        str_type,
        str_id,
        variable_dependencies,
        aggregate_mode,
        cur_variable_dependencies,
        always_add_variable_dependencies,
        total_count=0,
    ):
        """
        Special wrapper for the alldiff-predicate for the RS-Plus-Star method.
        """
        (
            rules_strings,
            rules_head_strings,
        ) = RSPlusStarHelper.rs_plus_star_generate_all_diff_rules(
            rule_head_name,
            count,
            elements,
            str_type,
            str_id,
            variable_dependencies,
            aggregate_mode,
            always_add_variable_dependencies,
            total_count=total_count,
        )

        count_name_ending = ""
        if len(always_add_variable_dependencies) == 0:
            if len(variable_dependencies) == 0:
                count_name_ending += "(1)"
            else:
                count_name_ending += f"({','.join(variable_dependencies)})"
        else:
            count_name_ending += f"({','.join(variable_dependencies + always_add_variable_dependencies)})"

        spawner_functions = []
        for variable in variable_dependencies:
            if variable in cur_variable_dependencies:
                cur_spawner_functions = cur_variable_dependencies[variable]
                for function in cur_spawner_functions:
                    spawner_functions.append(str(function))

        negated_head_strings = []
        for head_string in rules_head_strings:
            negated_head_strings.append(f"not {head_string}")

        helper_rule = (
            f"not_{rule_head_name}{count_name_ending} :- "
            + f"{','.join(spawner_functions + negated_head_strings)}."
        )

        rules_strings.append(helper_rule)

        return rules_strings
