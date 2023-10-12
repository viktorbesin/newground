import itertools
import clingo

from ..comparison_tools import ComparisonTools
from .rm_case import RMCase
from .count_aggregate_helper import CountAggregateHelper

from .aggregate_mode import AggregateMode

class RecursiveAggregateRewriting:

    @classmethod
    def recursive_strategy(cls, aggregate_index, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain, rule_positive_body, grounding_mode):

        new_rules, remaining_body_part, new_rules_set = cls.sum_aggregate(aggregate_index, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain, rule_positive_body, grounding_mode)

        return (new_rules, remaining_body_part, new_rules_set)

    @classmethod
    def sum_aggregate(cls, aggregate_index, aggregate_dict, variable_dependencies, aggregate_mode, cur_variable_dependencies, domain, rule_positive_body, grounding_mode):
        """
            Adds the necessary rules for the recursive sum aggregate.
        """

        new_prg_part = []
        new_prg_part_set = []
        remaining_body_part = []

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"] 


        # -------------------------------------------
        # Add tuple predicates

        max_number_element_head = 0
        skolem_constants = []

        for element_index in range(len(aggregate_dict["elements"])):

            element = aggregate_dict["elements"][element_index]

            if len(element["terms"]) > max_number_element_head:
                max_number_element_head = len(element["terms"])

        highest_integer_value = 0
        for domain_value in domain["0_terms"]:
            if CountAggregateHelper.check_string_is_int(str(domain_value)) == True:
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
                positive_body_string = ",".join([str(node) for node in rule_positive_body]) + ","
            else:
                positive_body_string = ""

            body_string = f"body_{str_type}_ag{str_id}({term_string}) :- {positive_body_string} {','.join(element['condition'])}."
            new_prg_part_set.append(body_string)


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

            body_heads_tuple_vars.append(','.join(element_tuples))
            body_heads.append(f"body_{str_type}_ag{str_id}({term_string})")

        if len(variable_dependencies) > 0:
            joined_variable_dependencies = "," + ','.join(variable_dependencies)
            first_tuple_predicate_arguments = f"{body_heads_tuple_vars[0]}{joined_variable_dependencies}"
            second_tuple_predicate_arguments = f"{body_heads_tuple_vars[1]}{joined_variable_dependencies}"
        else:
            joined_variable_dependencies = ""
            first_tuple_predicate_arguments = f"{body_heads_tuple_vars[0]}"
            second_tuple_predicate_arguments = f"{body_heads_tuple_vars[1]}"

        # -------------------------------------------
        # ADDED TO ORIGINAL BODY
        original_rule_aggregate_variable = f"S{str_id}"
        original_rule_aggregate = f"{str_type}_ag{str_id}({original_rule_aggregate_variable}{joined_variable_dependencies})"
        remaining_body_part.append(original_rule_aggregate)

        left_guard = aggregate_dict["left_guard"]
        if left_guard != None:
            left_guard_string = str(left_guard.term) 
            left_operator = ComparisonTools.getCompOperator(left_guard.comparison)
            remaining_body_part.append(f"{left_guard_string} {left_operator} {original_rule_aggregate_variable}")

        right_guard = aggregate_dict["right_guard"]
        if right_guard != None:
            right_guard_string = str(right_guard.term) 
            right_operator = ComparisonTools.getCompOperator(right_guard.comparison)
            remaining_body_part.append(f"{original_rule_aggregate_variable} {right_operator} {right_guard_string}")

        # -------------------------------------------
        # ADD RECURSIVE STUFF
        # Partial Last

        aggregate_head = f"{str_type}_ag{str_id}(S{joined_variable_dependencies})"
        rule_string = f"{aggregate_head} :- last_ag{str_id}({first_tuple_predicate_arguments}), partial_{str_type}_ag{str_id}({first_tuple_predicate_arguments},S)."
        new_prg_part.append(rule_string)

        # Partial Middle

        next_predicate = f"next_ag{str_id}({body_heads_tuple_vars[0]},{body_heads_tuple_vars[1]}{joined_variable_dependencies})"
        body_partial_predicate = f"partial_{str_type}_ag{str_id}({first_tuple_predicate_arguments},S1)"

        if str_type == "sum" or str_type == "count":
            partial_head = f"partial_{str_type}_ag{str_id}({second_tuple_predicate_arguments},S2)"
            if str_type == "sum":
                aggregate_expression = f"S2 = S1 + {body_heads_tuple_vars_first[1]}"
            elif str_type == "count":
                aggregate_expression = f"S2 = S1 + 1"

            rule_string = f"{partial_head} :- {next_predicate}, {body_partial_predicate}, {aggregate_expression}."
            new_prg_part.append(rule_string)
        elif str_type == "min" or str_type == "max":
            partial_head_1 = f"partial_{str_type}_ag{str_id}({second_tuple_predicate_arguments},S1)"
            partial_head_2 = f"partial_{str_type}_ag{str_id}({second_tuple_predicate_arguments},{body_heads_tuple_vars_first[1]})"

            if str_type == "max":
                aggregate_expression_1 = f"S1 > {body_heads_tuple_vars_first[1]}"
                aggregate_expression_2 = f"S1 <= {body_heads_tuple_vars_first[1]}"
            elif str_type == "min":
                aggregate_expression_1 = f"S1 < {body_heads_tuple_vars_first[1]}"
                aggregate_expression_2 = f"S1 >= {body_heads_tuple_vars_first[1]}"

            rule_string_1 = f"{partial_head_1} :- {next_predicate}, {body_partial_predicate}, {aggregate_expression_1}."
            rule_string_2 = f"{partial_head_2} :- {next_predicate}, {body_partial_predicate}, {aggregate_expression_2}."

            new_prg_part.append(rule_string_1)
            new_prg_part.append(rule_string_2)

        else:
            print("NOT IMPLEMENTED")
            assert(False)

        # Partial First
        partial_head = f"partial_{str_type}_ag{str_id}({first_tuple_predicate_arguments},S)"
        first_predicate = f"first_ag{str_id}({first_tuple_predicate_arguments})"

        if str_type == "sum" or str_type == "min" or str_type == "max":
            first_expression= f"S = {body_heads_tuple_vars_first[0]}"
        elif str_type == "count":
            first_expression= f"S = 1"

        rule_string = f"{partial_head} :- {first_predicate}, {first_expression}."
        new_prg_part.append(rule_string)

        # not_last
        not_last_head = f"not_last_ag{str_id}({first_tuple_predicate_arguments})"
        rule_string = f"{not_last_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[0]} < {body_heads[1]}."
        new_prg_part.append(rule_string)

        # Last
        last_head = f"last_ag{str_id}({first_tuple_predicate_arguments})"
        rule_string = f"{last_head} :- {body_heads[0]}, not not_last_ag{str_id}({first_tuple_predicate_arguments})."
        new_prg_part.append(rule_string)

        # not_next
        not_next_head = f"not_next_ag{str_id}({body_heads_tuple_vars[0]}, {body_heads_tuple_vars[1]}{joined_variable_dependencies})"
        not_next_comparisons = f"{body_heads[0]} < {body_heads[2]}, {body_heads[2]} < {body_heads[1]}."
        rule_string = f"{not_next_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[2]}, {not_next_comparisons}"
        new_prg_part.append(rule_string)

        # next
        next_head = f"next_ag{str_id}({body_heads_tuple_vars[0]}, {body_heads_tuple_vars[1]}{joined_variable_dependencies})"
        rule_string = f"{next_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[0]} < {body_heads[1]}, not not_next_ag{str_id}({body_heads_tuple_vars[0]}, {body_heads_tuple_vars[1]}{joined_variable_dependencies})."
        new_prg_part.append(rule_string)

        # not_first
        not_first_head = f"not_first_ag{str_id}({second_tuple_predicate_arguments})"
        rule_string = f"{not_first_head} :- {body_heads[0]}, {body_heads[1]}, {body_heads[0]} < {body_heads[1]}."
        new_prg_part.append(rule_string)

        # first
        first_head = f"first_ag{str_id}({first_tuple_predicate_arguments})"
        rule_string = f"{first_head} :- {body_heads[0]}, not not_first_ag{str_id}({first_tuple_predicate_arguments})."
        new_prg_part.append(rule_string)

        return (new_prg_part, remaining_body_part, new_prg_part_set)

