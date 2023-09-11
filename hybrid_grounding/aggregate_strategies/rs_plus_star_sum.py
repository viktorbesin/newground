import itertools
import clingo

from ..comparison_tools import ComparisonTools
from .rm_case import RMCase
from .count_aggregate_helper import CountAggregateHelper

from .aggregate_mode import AggregateMode

class RSPlusStarSum:

    @classmethod
    def _add_sum_aggregate_rules(cls, aggregate_dict, variable_dependencies, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string):
        
        new_prg_part_list = []
        new_prg_part_set = []

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"] 
        
        number_of_elements = len(aggregate_dict["elements"])

        original_rule_additional_body_literals = []

        if len(list(guard_domain)) == 1:
            guard_value = int(str(list(guard_domain)[0])) # Assuming constant

            cls._sum_single_domain_adder(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, [], guard_string)
        else:
            guard_domain_list = [int(value) for value in list(guard_domain)]

            for guard_value in guard_domain_list:
                always_add_variable_dependecies = [str(guard_value)]

                cls._sum_single_domain_adder(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, always_add_variable_dependecies, guard_string)

        return (new_prg_part_list, original_rule_additional_body_literals, list(set(new_prg_part_set)))
    
    @classmethod
    def _sum_single_domain_adder(cls, aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, always_add_variable_dependencies, guard_string):

            if aggregate_mode == AggregateMode.RS_STAR:
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

            sum = guard_value
            sum_predicate_name = f"{str_type}_ag{str_id}_{string_capsulation}"

            if operator_type in [">=",">","<=","<"]:
                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = f"({','.join(variable_dependencies + [guard_string])})" 

                if operator_type == ">=" or operator_type == ">":
                    # Monotone
                    double_negated_sum_predicate = f"not not_{sum_predicate_name}{arguments}"
                    original_rule_additional_body_literals.append(double_negated_sum_predicate)
                elif operator_type == "<=" or operator_type == "<":
                    # Anti-Monotone
                    triple_negated_sum_predicate = f"not not not_{sum_predicate_name}{arguments}"
                    original_rule_additional_body_literals.append(triple_negated_sum_predicate)

                if operator_type == "<":
                    sum = sum
                elif operator_type == ">=":
                    sum = sum
                elif operator_type == ">":
                    sum = sum + 1
                elif operator_type == "<=":
                    sum = sum + 1
                else:
                    assert(False) # Not implemented

                rules_strings = cls._sum_helper_level_2(sum_predicate_name, sum, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

            elif operator_type == "!=":
                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = f"({','.join(variable_dependencies + [guard_string])})" 

                double_negated_sum_predicate = f"not not_{sum_predicate_name}{arguments}"
                original_rule_additional_body_literals.append(double_negated_sum_predicate)

                #sum = int(str(list(guard_domain)[0])) # Assuming constant

                sum1 = sum
                sum2 = sum + 1

                rules_strings = cls._sum_helper_level_2(sum_predicate_name + "_1", sum1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)
                rules_strings += cls._sum_helper_level_2(sum_predicate_name + "_2", sum2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = f"({','.join(variable_dependencies + [str(guard_value)])})" 

                intermediate_rule = f"not_{sum_predicate_name}{arguments} :- not not_{sum_predicate_name}_1{arguments}, not_{sum_predicate_name}_2{arguments}."

                rules_strings.append(intermediate_rule)

            elif operator_type == "=":
                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = f"({','.join(variable_dependencies + [str(guard_string)])})" 
                        
                original_rule_additional_body_literals.append(f"not not_{sum_predicate_name}_1{arguments}")
                original_rule_additional_body_literals.append(f"not not not_{sum_predicate_name}_2{arguments}")

                sum1 = sum
                sum2 = sum + 1

                rules_strings = cls._sum_helper_level_2(sum_predicate_name + "_1", sum1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)
                rules_strings += cls._sum_helper_level_2(sum_predicate_name + "_2", sum2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)


                #rules_strings.append(intermediate_rule)
                
            else:
                print(f"Operator Type {operator_type} currently not supported!")
                raise Exception("Not supported operator type for aggregate!")

            for rule_string in rules_strings:
                new_prg_part_list.append(rule_string)

    @classmethod
    def _sum_helper_level_2(cls, rule_head_name, sum, elements, str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies):

        rules_strings = []
        rules_head_strings = []

        for secondary_guard_value in range(1, sum + 1):
            tmp_rules_strings, tmp_rules_head_strings = cls._sum_generate_bodies_and_helper_bodies(rule_head_name, secondary_guard_value, sum, elements, str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

            rules_strings += tmp_rules_strings
            rules_head_strings += tmp_rules_head_strings


        if len(always_add_variable_dependencies) == 0:
            sum_name_ending = ""
            if len(variable_dependencies) == 0:
                sum_name_ending += "(1)"
            else:
                sum_name_ending += f"({','.join(variable_dependencies + always_add_variable_dependencies)})"
        else:
            sum_name_ending = f"({','.join(variable_dependencies + always_add_variable_dependencies)})"

        spawner_functions = []
        for variable in variable_dependencies:
            if variable in cur_variable_dependencies:
                cur_spawner_functions = cur_variable_dependencies[variable]
                for function in cur_spawner_functions:
                    spawner_functions.append(str(function))

        negated_head_strings = []
        for head_string in rules_head_strings:
            negated_head_strings.append(f"not {head_string}")

        helper_rule = f"not_{rule_head_name}{sum_name_ending} :- {','.join(spawner_functions + negated_head_strings)}."

        rules_strings.append(helper_rule)

        return rules_strings
                
    @classmethod
    def _sum_generate_bodies_and_helper_bodies(cls, rule_head_name, current_number_of_predicate_tuples_considered, total_sum_value, elements, str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies):

        rules_strings = []
        rules_head_strings = []

        combination_lists = []
        for index in range(current_number_of_predicate_tuples_considered):
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
            terms = []
            bodies = []

            for index in range(current_number_of_predicate_tuples_considered):

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

                    bodies.append(f"{','.join(new_conditions)}")

            helper_bodies = []
            for index_1 in range(len(terms)):
                for index_2 in range(index_1 + 1, len(terms)):

                    helper_body = "0 != "

                    if len(terms[index_1]) != len(terms[index_2]):
                        continue

                    term_length = min(len(terms[index_1]), len(terms[index_2])) 

                    term_combinations = [] 
                    for term_index in range(term_length):
                        first_term = terms[index_1][term_index]
                        second_term = terms[index_2][term_index]

                        if CountAggregateHelper.check_string_is_int(first_term) == False and CountAggregateHelper.check_string_is_int(second_term) == False: 
                            term_combinations.append(f"({first_term} ^ {second_term})")

                    helper_body = f"0 != {'?'.join(term_combinations)}"
                    helper_bodies.append(helper_body)

            sum_up_list = [terms[index][0] for index in range(current_number_of_predicate_tuples_considered)]

            my_helper_sum = f"{total_sum_value} <= {'+'.join(sum_up_list)}"
            helper_bodies.append(my_helper_sum)

            if len(always_add_variable_dependencies) == 0:
                if len(combination_variables) == 0:
                    rule_head_ending = "(1)"
                else:
                    rule_head_ending = f"({','.join(combination_variables)})"
            else:
                rule_head_ending = f"({','.join(combination_variables + always_add_variable_dependencies)})"

            rule_head = f"{rule_head_name}_{current_number_of_predicate_tuples_considered}_{combination_index}{rule_head_ending}"
   
            rules_head_strings.append(rule_head) 
            rules_strings.append(f"{rule_head} :- {','.join(bodies + helper_bodies)}.")
            # END OF FOR LOOP
            # -----------------

        return (rules_strings, rules_head_strings)

