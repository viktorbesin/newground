import itertools
import clingo

from ..comparison_tools import ComparisonTools
from .rm_case import RMCase
from .count_aggregate_helper import CountAggregateHelper

from .aggregate_mode import AggregateMode


class RSPlusStarHelper:

    @classmethod
    def add_rs_star_tuple_predicate_rules(cls, aggregate_dict, str_type, str_id, variable_dependencies, new_prg_part_set, always_add_variable_dependencies):
        for element_index in range(len(aggregate_dict["elements"])):
            element = aggregate_dict["elements"][element_index]

            element_dependent_variables = []
            for variable in element["condition_variables"]:
                if variable in variable_dependencies:
                    element_dependent_variables.append(variable)

            for literal in always_add_variable_dependencies:
                element_dependent_variables.append(literal)

            term_string = f"{','.join(element['terms'] + element_dependent_variables)}"

            body_string = f"body_{str_type}_ag{str_id}_{element_index}({term_string}) :- {','.join(element['condition'])}."
            new_prg_part_set.append(body_string)

    @classmethod
    def _rs_plus_star_count_generate_bodies_and_helper_bodies(cls, rule_head_name, count, elements, str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies):
        """
        Generates the count-rule (alldiff-rule) for the RS-STAR and RS-PLUS aggregate-modes.
        """
        rules_strings = []
        rules_head_strings = []

        combination_lists = []
        for index in range(count):
            combination_lists.append(list(range(len(elements))))

        combination_list = list(itertools.product(*combination_lists))
        refined_combination_list = []
        for combination in combination_list:
            cur = list(combination)
            cur.sort()

            if cur not in refined_combination_list:
                refined_combination_list.append(cur)

        for combination_index in range(len(refined_combination_list)):

            combination = refined_combination_list[combination_index]

            combination_variables = []

            bodies, terms = cls.rs_plus_star_generate_bodies_alldiff_rule(count, elements, str_type, str_id, variable_dependencies, aggregate_mode, always_add_variable_dependencies, combination, combination_variables)

            helper_bodies = CountAggregateHelper.generate_all_diff_predicates(terms)

            if len(always_add_variable_dependencies) == 0:
                if len(combination_variables) == 0:
                    rule_head_ending = "(1)"
                else:
                    rule_head_ending = f"({','.join(combination_variables)})"
            else:
                rule_head_ending = f"({','.join(combination_variables + always_add_variable_dependencies)})"

            rule_head = f"{rule_head_name}_{combination_index}{rule_head_ending}"
   
            rules_head_strings.append(rule_head) 
            rules_strings.append(f"{rule_head} :- {','.join(bodies + helper_bodies)}.")
            # END OF FOR LOOP
            # -----------------

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

        helper_rule = f"not_{rule_head_name}{count_name_ending} :- {','.join(spawner_functions + negated_head_strings)}."

        rules_strings.append(helper_rule)

        return (rules_strings)


    @classmethod
    def rs_plus_star_generate_bodies_alldiff_rule(cls, count, elements, str_type, str_id, variable_dependencies, aggregate_mode, always_add_variable_dependencies, combination, combination_variables):
        bodies = []
        terms = []

        for index in range(count):
            element_index = combination[index]
            element = elements[element_index]

            element_dependent_variables = []
            for variable in element["condition_variables"]:
                if variable in variable_dependencies:
                    element_dependent_variables.append(variable)
                    if variable not in combination_variables:
                        combination_variables.append(variable)


            new_terms = []
            for term in element["terms"]:
                if CountAggregateHelper.check_string_is_int(str(term)) == True:
                    new_terms.append(str(term))
                else:
                    new_terms.append(f"{str(term)}_{str(element_index)}_{str(index)}")

            terms.append(new_terms)

            if aggregate_mode == AggregateMode.RS_STAR:
                terms_string = f"{','.join(new_terms + element_dependent_variables + always_add_variable_dependencies)}"
                bodies.append(f"body_{str_type}_ag{str_id}_{element_index}({terms_string})") 

            elif aggregate_mode == AggregateMode.RS_PLUS:
                terms_strings = cls._generate_rs_plus_alldiff_rules_bodies(element, element_dependent_variables, element_index, index)
                bodies.append(f"{','.join(terms_strings)}")

        return (bodies, terms)
    

    @classmethod
    def _generate_rs_plus_alldiff_rules_bodies(cls, element, element_dependent_variables, element_index, index):
        new_conditions = []

        for condition in element["condition"]:
            if "arguments" in condition:
                new_condition = condition["name"]

                new_args = []

                for argument in condition["arguments"]:
                    if "variable" in argument:
                        variable = argument["variable"]
                        if variable in element_dependent_variables:
                            new_args.append(f"{variable}")
                        else:
                            new_args.append(f"{variable}_{str(element_index)}_{str(index)}")
                    elif "term" in argument:
                        new_args.append(f"{argument['term']}")

                if len(new_args) > 0:
                    new_condition += f"({','.join(new_args)})"

                new_conditions.append(new_condition)
            elif "comparison" in condition:
                comparison = condition["comparison"]

                variable_assignments = {}

                left = comparison.term
                assert(len(comparison.guards) <= 1)
                right = comparison.guards[0].term
                comparison_operator = comparison.guards[0].comparison

                for argument in ComparisonTools.get_arguments_from_operation(left):
                    if argument.ast_type == clingo.ast.ASTType.Variable:
                        if str(argument) in element_dependent_variables:
                            variable_assignments[str(argument)] = f"{str(argument)}"
                        else:
                            variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}_{str(index)}"

                for argument in ComparisonTools.get_arguments_from_operation(right):
                    if argument.ast_type == clingo.ast.ASTType.Variable:
                        if str(argument) in element_dependent_variables:
                            variable_assignments[str(argument)] = f"{str(argument)}"
                        else:
                            variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}_{str(index)}"

                instantiated_left = ComparisonTools.instantiate_operation(left, variable_assignments)
                instantiated_right = ComparisonTools.instantiate_operation(right, variable_assignments)

                new_conditions.append(ComparisonTools.comparison_handlings(comparison_operator, instantiated_left, instantiated_right))
            else:
                assert(False) # Not implemented

        return new_conditions