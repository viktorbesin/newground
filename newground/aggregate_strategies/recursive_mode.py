"""
Module for the recursive strategies.
"""

from ..comparison_tools import ComparisonTools
from .count_aggregate_helper import CountAggregateHelper


class RecursiveAggregateRewriting:
    """
    Class for the recursive strategies.
    """

    @classmethod
    def recursive_strategy(
        cls,
        aggregate_dict,
        variables_dependencies_aggregate,
        domain,
        rule_positive_body,
    ):
        """
        Wrapper method for the recursive aggregate generator.
        """
        new_rules, remaining_body_part, new_rules_set = cls.generate_aggregate(
            aggregate_dict,
            variables_dependencies_aggregate,
            domain,
            rule_positive_body,
        )

        return (new_rules, remaining_body_part, new_rules_set)

    @classmethod
    def generate_aggregate(
        cls,
        aggregate_dict,
        variable_dependencies,
        domain,
        rule_positive_body,
    ):
        """
        Adds the necessary rules for the recursive aggregate.
        """

        new_prg_part = []
        new_prg_part_set = []
        remaining_body_part = []

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"]

        (
            skolem_constants,
            element_dependent_variables,
        ) = cls.generate_tuple_predicate_rules(
            aggregate_dict,
            variable_dependencies,
            domain,
            rule_positive_body,
            new_prg_part_set,
            str_type,
            str_id,
        )

        (
            body_heads,
            body_heads_tuple_vars,
            body_heads_tuple_vars_first,
            joined_variable_dependencies,
            first_tuple_predicate_arguments,
            second_tuple_predicate_arguments,
        ) = cls.generate_helper_variables(
            variable_dependencies,
            str_type,
            str_id,
            skolem_constants,
            element_dependent_variables,
        )

        cls.added_to_original_body(
            str_id,
            str_type,
            joined_variable_dependencies,
            remaining_body_part,
            aggregate_dict,
        )

        cls.add_partial_predicate_rules(
            str_type,
            str_id,
            joined_variable_dependencies,
            first_tuple_predicate_arguments,
            body_heads_tuple_vars,
            second_tuple_predicate_arguments,
            body_heads_tuple_vars_first,
            new_prg_part,
        )

        cls.generate_ordering_predicate_rules(
            body_heads,
            str_id,
            joined_variable_dependencies,
            first_tuple_predicate_arguments,
            body_heads_tuple_vars,
            second_tuple_predicate_arguments,
            new_prg_part,
        )

        return (new_prg_part, remaining_body_part, new_prg_part_set)

    @classmethod
    def generate_helper_variables(
        cls,
        variable_dependencies,
        str_type,
        str_id,
        skolem_constants,
        element_dependent_variables,
    ):
        """
        Generate the helper variables, needed by the other construction methods.
        """

        body_heads = []
        body_heads_tuple_vars = []
        body_heads_tuple_vars_first = []
        for index in range(3):
            element_tuples = []
            for tuple_index in range(len(skolem_constants)):
                cur_variable = f"TUPLEVARIABLE_{index}_{tuple_index}"
                element_tuples.append(cur_variable)

                if tuple_index == 0:
                    body_heads_tuple_vars_first.append(cur_variable)

            term_string = f"{','.join(element_tuples + element_dependent_variables)}"

            body_heads_tuple_vars.append(",".join(element_tuples))
            body_heads.append(f"body_{str_type}_ag{str_id}({term_string})")

        if len(variable_dependencies) > 0:
            joined_variable_dependencies = "," + ",".join(variable_dependencies)
            first_tuple_predicate_arguments = (
                f"{body_heads_tuple_vars[0]}{joined_variable_dependencies}"
            )
            second_tuple_predicate_arguments = (
                f"{body_heads_tuple_vars[1]}{joined_variable_dependencies}"
            )
        else:
            joined_variable_dependencies = ""
            first_tuple_predicate_arguments = f"{body_heads_tuple_vars[0]}"
            second_tuple_predicate_arguments = f"{body_heads_tuple_vars[1]}"
        return (
            body_heads,
            body_heads_tuple_vars,
            body_heads_tuple_vars_first,
            joined_variable_dependencies,
            first_tuple_predicate_arguments,
            second_tuple_predicate_arguments,
        )

    @classmethod
    def generate_tuple_predicate_rules(
        cls,
        aggregate_dict,
        variable_dependencies,
        domain,
        rule_positive_body,
        new_prg_part_set,
        str_type,
        str_id,
    ):
        """
        Generate the tuple predicates and rules.
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

        for element_index in range(len(aggregate_dict["elements"])):
            element = aggregate_dict["elements"][element_index]

            element_tuples = []

            for skolem_index in range(max_number_element_head):
                if skolem_index < len(element["terms"]):
                    element_tuples.append(element["terms"][skolem_index])
                else:
                    element_tuples.append(skolem_constants[skolem_index])

            element_dependent_variables = variable_dependencies.copy()

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
        return skolem_constants, element_dependent_variables

    @classmethod
    def added_to_original_body(
        cls,
        str_id,
        str_type,
        joined_variable_dependencies,
        remaining_body_part,
        aggregate_dict,
    ):
        """
        Handle the rewriting of the original rule.
        """
        original_rule_aggregate_variable = f"S{str_id}"
        original_rule_aggregate = (
            f"{str_type}_ag{str_id}"
            + f"({original_rule_aggregate_variable}{joined_variable_dependencies})"
        )
        remaining_body_part.append(original_rule_aggregate)

        left_guard = aggregate_dict["left_guard"]
        if left_guard is not None:
            left_guard_string = str(left_guard.term)
            left_operator = ComparisonTools.get_comp_operator(left_guard.comparison)
            remaining_body_part.append(
                f"{left_guard_string} {left_operator} {original_rule_aggregate_variable}"
            )

        right_guard = aggregate_dict["right_guard"]
        if right_guard is not None:
            right_guard_string = str(right_guard.term)
            right_operator = ComparisonTools.get_comp_operator(right_guard.comparison)
            remaining_body_part.append(
                f"{original_rule_aggregate_variable} {right_operator} {right_guard_string}"
            )

    @classmethod
    def add_partial_predicate_rules(
        cls,
        str_type,
        str_id,
        joined_variable_dependencies,
        first_tuple_predicate_arguments,
        body_heads_tuple_vars,
        second_tuple_predicate_arguments,
        body_heads_tuple_vars_first,
        new_prg_part,
    ):
        """
        Add all 'partial' predicate rules.
        """

        aggregate_head = f"{str_type}_ag{str_id}(S{joined_variable_dependencies})"
        rule_string = (
            f"{aggregate_head} :- last_ag{str_id}({first_tuple_predicate_arguments}), "
            + f"partial_{str_type}_ag{str_id}({first_tuple_predicate_arguments},S)."
        )
        new_prg_part.append(rule_string)

        # Partial Middle

        next_predicate = (
            f"next_ag{str_id}"
            + f"({body_heads_tuple_vars[0]},{body_heads_tuple_vars[1]}{joined_variable_dependencies})"
        )
        body_partial_predicate = (
            f"partial_{str_type}_ag{str_id}({first_tuple_predicate_arguments},S1)"
        )

        if str_type in ["sum", "count"]:
            partial_head = (
                f"partial_{str_type}_ag{str_id}({second_tuple_predicate_arguments},S2)"
            )
            if str_type == "sum":
                aggregate_expression = f"S2 = S1 + {body_heads_tuple_vars_first[1]}"
            elif str_type == "count":
                aggregate_expression = "S2 = S1 + 1"

            rule_string = f"{partial_head} :- {next_predicate}, {body_partial_predicate}, {aggregate_expression}."
            new_prg_part.append(rule_string)
        elif str_type in ["min", "max"]:
            partial_head_1 = (
                f"partial_{str_type}_ag{str_id}({second_tuple_predicate_arguments},S1)"
            )
            partial_head_2 = (
                f"partial_{str_type}_ag{str_id}"
                + f"({second_tuple_predicate_arguments},{body_heads_tuple_vars_first[1]})"
            )

            if str_type == "max":
                aggregate_expression_1 = f"S1 > {body_heads_tuple_vars_first[1]}"
                aggregate_expression_2 = f"S1 <= {body_heads_tuple_vars_first[1]}"
            elif str_type == "min":
                aggregate_expression_1 = f"S1 < {body_heads_tuple_vars_first[1]}"
                aggregate_expression_2 = f"S1 >= {body_heads_tuple_vars_first[1]}"

            rule_string_1 = (
                f"{partial_head_1} :- {next_predicate}, {body_partial_predicate}, "
                + f"{aggregate_expression_1}."
            )
            rule_string_2 = (
                f"{partial_head_2} :- {next_predicate}, {body_partial_predicate}, "
                + f"{aggregate_expression_2}."
            )

            new_prg_part.append(rule_string_1)
            new_prg_part.append(rule_string_2)

        else:
            print("NOT IMPLEMENTED")
            assert False

        # Partial First
        partial_head = (
            f"partial_{str_type}_ag{str_id}({first_tuple_predicate_arguments},S)"
        )
        first_predicate = f"first_ag{str_id}({first_tuple_predicate_arguments})"

        if str_type in ["sum", "min", "max"]:
            first_expression = f"S = {body_heads_tuple_vars_first[0]}"
        elif str_type == "count":
            first_expression = "S = 1"

        rule_string = f"{partial_head} :- {first_predicate}, {first_expression}."
        new_prg_part.append(rule_string)

    @classmethod
    def generate_ordering_predicate_rules(
        cls,
        body_heads,
        str_id,
        joined_variable_dependencies,
        first_tuple_predicate_arguments,
        body_heads_tuple_vars,
        second_tuple_predicate_arguments,
        new_prg_part,
    ):
        """
        Generate all predicates/rules which are needed for the ordering.
        """

        # not_last
        not_last_head = f"not_last_ag{str_id}({first_tuple_predicate_arguments})"
        rule_string = f"{not_last_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[0]} < {body_heads[1]}."
        new_prg_part.append(rule_string)

        # Last
        last_head = f"last_ag{str_id}({first_tuple_predicate_arguments})"
        rule_string = f"{last_head} :- {body_heads[0]}, not not_last_ag{str_id}({first_tuple_predicate_arguments})."
        new_prg_part.append(rule_string)

        # not_next
        not_next_head = (
            f"not_next_ag{str_id}"
            + f"({body_heads_tuple_vars[0]}, {body_heads_tuple_vars[1]}{joined_variable_dependencies})"
        )
        not_next_comparisons = (
            f"{body_heads[0]} < {body_heads[2]}, {body_heads[2]} < {body_heads[1]}."
        )
        rule_string = f"{not_next_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[2]}, {not_next_comparisons}"
        new_prg_part.append(rule_string)

        # next
        next_head = (
            f"next_ag{str_id}"
            + f"({body_heads_tuple_vars[0]}, {body_heads_tuple_vars[1]}{joined_variable_dependencies})"
        )
        rule_string = (
            f"{next_head} :- {body_heads[0]}, {body_heads[1]}, "
            + f"{body_heads[0]} < {body_heads[1]}, not not_next_ag{str_id}({body_heads_tuple_vars[0]}, "
            + f"{body_heads_tuple_vars[1]}{joined_variable_dependencies})."
        )
        new_prg_part.append(rule_string)

        # not_first
        not_first_head = f"not_first_ag{str_id}({second_tuple_predicate_arguments})"
        rule_string = f"{not_first_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[0]} < {body_heads[1]}."
        new_prg_part.append(rule_string)

        # first
        first_head = f"first_ag{str_id}({first_tuple_predicate_arguments})"
        rule_string = f"{first_head} :- {body_heads[0]}, not not_first_ag{str_id}({first_tuple_predicate_arguments})."
        new_prg_part.append(rule_string)
