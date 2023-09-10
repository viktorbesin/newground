
import itertools
import clingo

from ..comparison_tools import ComparisonTools
from .rm_case import RMCase

from .aggregate_mode import AggregateMode

class RSPlusStarRewriting:

    @classmethod
    def rewriting_aggregate_strategy(cls, aggregate_index, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain):

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"] 

        new_prg_list = []
        new_prg_set = []
        output_remaining_body = []


        if aggregate_dict["left_guard"]:    
            left_guard = aggregate_dict["left_guard"]
            left_guard_string = str(left_guard.term) 

            left_guard_domain = cls.get_guard_domain(cur_variable_dependencies, domain, left_guard, left_guard_string, variables_dependencies_aggregate, aggregate_dict)
                
            operator = ComparisonTools.getCompOperator(left_guard.comparison)
            
            if operator == "<":
                operator_type = ">"
            elif operator == "<=":
                operator_type = ">="
            elif operator == ">":
                operator_type = "<" 
            elif operator == ">=":
                operator_type = "<="
            else:
                operator_type = operator

            string_capsulation = "left"

            (new_prg_list_tmp, output_remaining_body_tmp, new_prg_set_tmp) = cls.aggregate_caller(str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, left_guard_domain, operator_type, string_capsulation, left_guard_string)

            new_prg_list += new_prg_list_tmp
            output_remaining_body += output_remaining_body_tmp
            new_prg_set += new_prg_set_tmp

        if aggregate_dict["right_guard"]:    
            right_guard = aggregate_dict["right_guard"]
            right_guard_string = str(right_guard.term) 

            right_guard_domain = cls.get_guard_domain(cur_variable_dependencies, domain, right_guard, right_guard_string, variables_dependencies_aggregate, aggregate_dict)
                
            operator = ComparisonTools.getCompOperator(right_guard.comparison)
            operator_type = operator

            string_capsulation = "right"

            (new_prg_list_tmp, output_remaining_body_tmp, new_prg_set_tmp) = cls.aggregate_caller(str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, right_guard_domain, operator_type, string_capsulation, left_guard_string)

            new_prg_list += new_prg_list_tmp
            output_remaining_body += output_remaining_body_tmp
            new_prg_set += new_prg_set_tmp

        return (new_prg_list, output_remaining_body, list(set(new_prg_set)))
   
    @classmethod
    def aggregate_caller(cls, str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string):

        if str_type == "count":
            new_prg_list, output_remaining_body, new_prg_set = cls._add_count_aggregate_rules(aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string)
        else:
            assert(False)

        return (new_prg_list, output_remaining_body, new_prg_set)

    @classmethod
    def get_guard_domain(cls, cur_variable_dependencies, domain, guard, guard_string, variable_dependencies_aggregate, aggregate_dict):

        if guard_string in cur_variable_dependencies:
            # Guard is a Variable
            guard_domain = None

            operator = ComparisonTools.getCompOperator(guard.comparison)

            if operator != "=":
                for var_dependency in cur_variable_dependencies[guard_string]:
                    var_dependency_argument_position = -1
                    var_dependency_argument_position_counter = 0
                    for argument in var_dependency.arguments:
                        if str(argument) == guard_string:
                            var_dependency_argument_position = var_dependency_argument_position_counter
                            break

                        var_dependency_argument_position_counter += 1

                    cur_var_dependency_domain = set(domain[var_dependency.name][str(var_dependency_argument_position)])

                    if guard_domain is None:
                        guard_domain = cur_var_dependency_domain
                    else:
                        guard_domain = set(guard_domain).intersection(cur_var_dependency_domain)
            else:
                print("Equality with Variable not Implemented!")
                raise Exception("Equality with Variable not Implemented!")

        else:
            # Otherwise assuming int, will fail if e.g. is comparison or something else
            guard_domain = [int(str(guard.term))]
        return guard_domain

    @classmethod
    def rewriting_no_body_aggregate_strategy(cls, aggregate, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain):

        new_prg_list = []
        output_remaining_body = []
        new_prg_set = []

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        if str_type == "count":
            count_name_ending = ""
            if len(variables_dependencies_aggregate) == 0:
                count_name_ending += "(1)"
            else:
                count_name_ending += f"({','.join(variables_dependencies_aggregate)})"


            if aggregate["left_guard"]:
                left_name = f"not not_{str_type}_ag{str_id}_left{count_name_ending}"
                output_remaining_body.append(left_name)
            if aggregate["right_guard"]:
                right_name = f"not not not_{str_type}_ag{str_id}_right{count_name_ending}"
                output_remaining_body.append(right_name)

            new_prg_list += cls._add_count_aggregate_rules(aggregate, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies)

        elif str_type == "min":
            (new_prg_list_tmp, output_remaining_body_tmp) = cls._add_min_max_aggregate_rules(aggregate, variables_dependencies_aggregate, cls._min_operator_functions, cls._min_remaining_body_functions, aggregate_mode, cur_variable_dependencies)
            new_prg_list += new_prg_list_tmp
            output_remaining_body += output_remaining_body_tmp
        elif str_type == "max":
            (new_prg_list_tmp, output_remaining_body_tmp) = cls._add_min_max_aggregate_rules(aggregate, variables_dependencies_aggregate, cls._max_operator_functions, cls._max_remaining_body_functions, aggregate_mode, cur_variable_dependencies)
            new_prg_list += new_prg_list_tmp
            output_remaining_body += output_remaining_body_tmp

        return (new_prg_list, output_remaining_body, list(set(new_prg_set)))

    #--------------------------------------------------------------------------------------------------------
    #------------------------------------ MIN-MAX-PART ------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------

    @classmethod
    def _max_operator_functions(cls, operator_side, operator):
        if operator_side == "left":
            if operator == "<":
                new_operator = ">"
            elif operator == "<=":
                new_operator = ">="
            else:
                assert(False) # Not implemented
        elif operator_side == "right":
            if operator == "<":
                new_operator = ">="
            elif operator == "<=":
                new_operator = ">"
            else:
                assert(False) # Not implemented
        else:
            assert(False) 

        return new_operator


    @classmethod
    def _max_remaining_body_functions(cls, operator_side, head_count, name):
        if operator_side == "left":
            if head_count > 1:
                string =  f"not {name}"
            elif head_count == 1:
                string = f"{name}"
            else:
                assert(False)
        elif operator_side == "right":
            if head_count > 1:
                string = f"not not {name}"
            elif head_count == 1:
                string = f"not {name}"
        else:
            assert(False)

        return string

    @classmethod
    def _min_operator_functions(cls, operator_side, operator):
        if operator_side == "left":
            if operator == "<":
                new_operator = "<="
            elif operator == "<=":
                new_operator = "<"
            else:
                assert(False) # Not implemented
        elif operator_side == "right":
            if operator == "<":
                new_operator = "<"
            elif operator == "<=":
                new_operator = "<="
            else:
                assert(False) # Not implemented
        else:
            assert(False) 

        return new_operator

    @classmethod
    def _min_remaining_body_functions(cls, operator_side, head_count, name):
        if operator_side == "left":
            if head_count > 1:
                string =  f"not not {name}"
            elif head_count == 1:
                string = f"not {name}"
            else:
                assert(False)
        elif operator_side == "right":
            if head_count > 1:
                string = f"not {name}"
            elif head_count == 1:
                string = f"{name}"
        else:
            assert(False)

        return string


    @classmethod
    def _add_min_max_aggregate_rules(cls, aggregate, variable_dependencies, new_operator_functions, remaining_body_functions, aggregate_mode, cur_variable_dependencies):

        new_prg_list = []

        elements = aggregate["elements"]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        remaining_body = []
        element_predicate_names = []

        left_head_names = []
        right_head_names = []

        for element_index in range(len(elements)):

            element = elements[element_index]
            element_dependent_variables = []

            for variable in element["condition_variables"]:
                if variable in variable_dependencies:
                    element_dependent_variables.append(variable)

            terms = element["terms"]

            if aggregate_mode == AggregateMode.RS_STAR:

                element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"

                terms_string = f"{','.join(terms + element_dependent_variables)}"

                element_body = f"{element_predicate_name}({terms_string})"
                body_string = f"{element_body} :- {','.join(element['condition'])}."

                new_prg_list.append(body_string)

                element_predicate_names.append(element_predicate_name)

            new_prg_list.append(f"#program {str_type}.")

            if len(element_dependent_variables) == 0:
                rule_head_ending = "(1)"
            else:
                rule_head_ending = f"({','.join(element_dependent_variables)})"

            if aggregate["left_guard"]:
                left_guard = aggregate["left_guard"]


                left_name = f"{str_type}_ag{str_id}_left"
                left_head_name = f"{left_name}_{element_index}{rule_head_ending}"

                left_guard_term = str(left_guard.term)
                count = int(left_guard_term) # Assuming constant

                operator = ComparisonTools.getCompOperator(left_guard.comparison)

                new_operator = new_operator_functions("left", operator)

                bodies = cls._add_min_max_aggregate_helper(element, element_index, new_operator, left_guard_term, element_predicate_names, element_dependent_variables, aggregate_mode, cur_variable_dependencies)


                rule_string = f"{left_head_name} :- {','.join(bodies)}."

                left_head_names.append(left_head_name)

                new_prg_list.append(rule_string)
            
            if aggregate["right_guard"]:
                right_guard = aggregate["right_guard"]

                right_name = f"{str_type}_ag{str_id}_right"
                right_head_name = f"{right_name}_{element_index}{rule_head_ending}"

                right_guard_term = str(right_guard.term)
                count = int(right_guard_term) # Assuming constant

                operator = ComparisonTools.getCompOperator(right_guard.comparison)

                new_operator = new_operator_functions("right", operator)

                bodies = cls._add_min_max_aggregate_helper(element, element_index, new_operator, right_guard_term, element_predicate_names, element_dependent_variables, aggregate_mode, cur_variable_dependencies)


                rule_string = f"{right_head_name} :- {','.join(bodies)}."
                
                right_head_names.append(right_head_name)

                new_prg_list.append(rule_string)


        if len(variable_dependencies) == 0:
            rule_head_ending = "(1)"
        else:
            rule_head_ending = f"({','.join(variable_dependencies)})"

        spawner_functions = []
        for variable in variable_dependencies:
            if variable in cur_variable_dependencies:
                cur_spawner_functions = cur_variable_dependencies[variable]
                for function in cur_spawner_functions:
                    spawner_functions.append(str(function))

        if len(left_head_names) > 1:
            left_intermediate_rule = f"not_{left_name}{rule_head_ending}"

            negated_head_strings = []
            for left_name in left_head_names:
                negated_head_strings.append(f"not {left_name}")

            helper_rule = f"{left_intermediate_rule} :- {','.join(spawner_functions + negated_head_strings)}."
            new_prg_list.append(helper_rule)
            remaining_body.append(remaining_body_functions("left",len(left_head_names),left_intermediate_rule))
        elif len(left_head_names) == 1:
            remaining_body.append(remaining_body_functions("left",len(left_head_names),left_head_names[0]))

        if len(right_head_names) > 1:
            right_intermediate_rule = f"not_{right_name}{rule_head_ending}"

            negated_head_strings = []
            for right_name in right_head_names:
                negated_head_strings.append(f"not {right_name}")

            helper_rule = f"{right_intermediate_rule} :- {','.join(spawner_functions + negated_head_strings)}."
            new_prg_list.append(helper_rule)

            remaining_body.append(remaining_body_functions("right",len(left_head_names),right_intermediate_rule))
        elif len(right_head_names) == 1:
            remaining_body.append(remaining_body_functions("right",len(left_head_names),right_head_names[0]))

        return (new_prg_list, remaining_body)
 
    @classmethod
    def _add_min_max_aggregate_helper(cls, element, element_index, new_operator, guard_term, element_predicate_names, element_dependent_variables, aggregate_mode, cur_variable_dependencies):

        bodies = []

        terms = []
        for term in element["terms"]:
            terms.append(f"{term}_{str(element_index)}")

        terms += element_dependent_variables

        if aggregate_mode == AggregateMode.RS_STAR:
            body = f"{element_predicate_names[element_index]}({','.join(terms)}), {terms[0]} {new_operator} {guard_term}"
            bodies.append(body)

        elif aggregate_mode == AggregateMode.RS_PLUS:

            new_conditions = []
            for condition in element["condition"]:
                if "arguments" in condition: # is a function

                    new_arguments = []
                    for argument in condition["arguments"]:
                        if "variable" in argument:
                            variable = argument['variable']
                            if str(variable) in element_dependent_variables:
                                new_arguments.append(str(variable))
                            else:
                                new_arguments.append(f"{str(variable)}_{element_index}")
                        elif "term" in argument:
                            new_arguments.append(f"{argument['term']}")
                        else:
                            assert(False) # Not implemented

                    condition_string = f"{condition['name']}"
                    if len(new_arguments) > 0:
                        condition_string += f"({','.join(new_arguments)})"

                    new_conditions.append(condition_string)

                elif "comparison" in condition: # is a comparison
                    comparison = condition["comparison"]

                    variable_assignments = {}

                    left = comparison.term
                    assert(len(comparison.guards) <= 1)
                    right = comparison.guards[0].term
                    comparison_operator = comparison.guards[0].comparison



                    for argument in ComparisonTools.get_arguments_from_operation(left):
                        if argument.ast_type == clingo.ast.ASTType.Variable:
                            if str(argument) in element_dependent_variables:
                                variable_assignments[str(argument)] = str(argument)
                            else:
                                variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}"

                    for argument in ComparisonTools.get_arguments_from_operation(right):
                        if argument.ast_type == clingo.ast.ASTType.Variable:
                            if str(argument) in element_dependent_variables:
                                variable_assignments[str(argument)] = str(argument)
                            else:
                                variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}"

                    instantiated_left = ComparisonTools.instantiate_operation(left, variable_assignments)
                    instantiated_right = ComparisonTools.instantiate_operation(right, variable_assignments)

                    new_conditions.append(ComparisonTools.comparison_handlings(comparison_operator, instantiated_left, instantiated_right))

                else:
                    assert(False) # Not implemented

            new_conditions.append(f"{terms[0]} {new_operator} {guard_term}")

            bodies += new_conditions

        return bodies
 
    #--------------------------------------------------------------------------------------------------------
    #------------------------------------ COUNT-PART --------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------


    @classmethod
    def _add_count_aggregate_rules(cls, aggregate_dict, variable_dependencies, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string):
        
        new_prg_part_list = []
        new_prg_part_set = []

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"] 
        
        number_of_elements = len(aggregate_dict["elements"])

        original_rule_additional_body_literals = []

        if number_of_elements == 1 and (operator_type == ">=" or ">") and len(list(guard_domain)) == 1:
            # Handle special case RM (RM from paper)
            original_rule_additional_body_literals += RMCase._handle_rm_case(aggregate_dict, variable_dependencies, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type)

        elif aggregate_mode == AggregateMode.RS_STAR or aggregate_mode == AggregateMode.RS_PLUS: 

            if len(list(guard_domain)) == 1:
                guard_value = int(str(list(guard_domain)[0])) # Assuming constant

                cls._count_single_domain_adder(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, [], guard_string)
            else:
                guard_domain_list = [int(value) for value in list(guard_domain)]

                for guard_value in guard_domain_list:
                    always_add_variable_dependecies = [str(guard_value)]

                    cls._count_single_domain_adder(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, always_add_variable_dependecies, guard_string)



        return (new_prg_part_list, original_rule_additional_body_literals, list(set(new_prg_part_set)))
    
    @classmethod
    def _count_single_domain_adder(cls, aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, always_add_variable_dependencies, guard_string):

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
 

            count = guard_value
            count_predicate_name = f"{str_type}_ag{str_id}_{string_capsulation}"

            if operator_type in [">=",">","<=","<"]:
                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies + [guard_string])})" 

                if operator_type == ">=" or operator_type == ">":
                    # Monotone
                    double_negated_count_predicate = f"not not_{count_predicate_name}{arguments}"
                    original_rule_additional_body_literals.append(double_negated_count_predicate)
                elif operator_type == "<=" or operator_type == "<":
                    # Anti-Monotone
                    triple_negated_count_predicate = f"not not not_{count_predicate_name}{arguments}"
                    original_rule_additional_body_literals.append(triple_negated_count_predicate)

                if operator_type == "<":
                    count = count
                elif operator_type == ">=":
                    count = count
                elif operator_type == ">":
                    count = count + 1
                elif operator_type == "<=":
                    count = count + 1
                else:
                    assert(False) # Not implemented

                rules_strings = cls._count_generate_bodies_and_helper_bodies(count_predicate_name, count, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

            elif operator_type == "!=":
                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies + [guard_string])})" 

                double_negated_count_predicate = f"not not_{count_predicate_name}{arguments}"
                original_rule_additional_body_literals.append(double_negated_count_predicate)

                #count = int(str(list(guard_domain)[0])) # Assuming constant

                count1 = count
                count2 = count + 1

                rules_strings = cls._count_generate_bodies_and_helper_bodies(count_predicate_name + "_1", count1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)
                rules_strings += cls._count_generate_bodies_and_helper_bodies(count_predicate_name + "_2", count2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

                if len(always_add_variable_dependencies) == 0:
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies)})" 
                else:
                    # Special case if guard is variable
                    arguments = ""
                    if len(variable_dependencies) == 0:
                        arguments += "(1)"
                    else:
                        arguments += f"({','.join(variable_dependencies + [str(guard_value)])})" 

                intermediate_rule = f"not_{count_predicate_name}{arguments} :- not not_{count_predicate_name}_1{arguments}, not_{count_predicate_name}_2{arguments}."

                rules_strings.append(intermediate_rule)

            elif operator_type == "=":
                arguments = ""
                if len(variable_dependencies) == 0:
                    arguments += "(1)"
                else:
                    arguments += f"({','.join(variable_dependencies)})" 

                count1 = count
                count2 = count + 1

                rules_strings = cls._count_generate_bodies_and_helper_bodies(count_predicate_name + "_1", count1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)
                rules_strings += cls._count_generate_bodies_and_helper_bodies(count_predicate_name + "_2", count2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

                original_rule_additional_body_literals.append(f"not not_{count_predicate_name}_1{arguments}")
                original_rule_additional_body_literals.append(f"not not not_{count_predicate_name}_2{arguments}")

                #rules_strings.append(intermediate_rule)
                
            else:
                print(f"Operator Type {operator_type} currently not supported!")
                raise Exception("Not supported operator type for aggregate!")

            for rule_string in rules_strings:
                new_prg_part_list.append(rule_string)
                
    @classmethod
    def _count_generate_bodies_and_helper_bodies(cls, rule_head_name, count, elements, str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies):

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
            terms = []
            bodies = []

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
                    if cls.check_string_is_int(str(term)) == True:
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
                                        new_args.append(f"{str(argument)}")
                                    else:
                                        new_args.append(f"{str(argument)}_{str(element_index)}_{str(index)}")

                                    variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}_{str(index)}"

                            for argument in ComparisonTools.get_arguments_from_operation(right):
                                if argument.ast_type == clingo.ast.ASTType.Variable:
                                    if str(argument) in element_dependent_variables:
                                        new_args.append(f"{str(argument)}")
                                    else:
                                        new_args.append(f"{str(argument)}_{str(element_index)}_{str(index)}")

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

                        if cls.check_string_is_int(first_term) == False and cls.check_string_is_int(second_term) == False: 
                            term_combinations.append(f"({first_term} ^ {second_term})")

                    helper_body = f"0 != {'?'.join(term_combinations)}"
                    helper_bodies.append(helper_body)

            if len(combination_variables) == 0:
                rule_head_ending = "(1)"
            else:
                rule_head_ending = f"({','.join(combination_variables + always_add_variable_dependencies)})"

            rule_head = f"{rule_head_name}_{combination_index}{rule_head_ending}"
   
            rules_head_strings.append(rule_head) 
            rules_strings.append(f"{rule_head} :- {','.join(bodies + helper_bodies)}.")
            # END OF FOR LOOP
            # -----------------

        count_name_ending = ""
        if len(variable_dependencies) == 0:
            count_name_ending += "(1)"
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
    def check_string_is_int(cls, string):
        try:
            a = int(string, 10)
            return True
        except ValueError:
            return False
