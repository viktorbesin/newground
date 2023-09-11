
import clingo

from ..comparison_tools import ComparisonTools

from .aggregate_mode import AggregateMode
from .rs_plus_star_count import RSPlusStarCount
from .count_aggregate_helper import CountAggregateHelper
from .rs_plus_star_min_max import RSPlusStarMinMax
from .rs_plus_star_sum import RSPlusStarSum

class RSPlusStarRewriting:

    @classmethod
    def rewriting_aggregate_strategy(cls, aggregate_index, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain, rule_positive_body):

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

            (new_prg_list_tmp, output_remaining_body_tmp, new_prg_set_tmp) = cls.aggregate_caller(str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, left_guard_domain, operator_type, string_capsulation, left_guard_string, rule_positive_body)

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

            (new_prg_list_tmp, output_remaining_body_tmp, new_prg_set_tmp) = cls.aggregate_caller(str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, right_guard_domain, operator_type, string_capsulation, left_guard_string, rule_positive_body)

            new_prg_list += new_prg_list_tmp
            output_remaining_body += output_remaining_body_tmp
            new_prg_set += new_prg_set_tmp

        return (new_prg_list, list(set(output_remaining_body)), list(set(new_prg_set)))
   
    @classmethod
    def aggregate_caller(cls, str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string, rule_positive_body):

        if str_type == "count":
            new_prg_list, output_remaining_body, new_prg_set = RSPlusStarCount._add_count_aggregate_rules(aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string)
        elif str_type == "max" or str_type == "min":
            new_prg_list, output_remaining_body, new_prg_set = RSPlusStarMinMax._add_min_max_aggregate_rules(str_type, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string, rule_positive_body)
        elif str_type == "sum":
            new_prg_list, output_remaining_body, new_prg_set = RSPlusStarSum._add_sum_aggregate_rules(aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string)
        else:
            raise Exception("NOT IMPLMENTED AGGREGATE TYPE: " + str_type)

        return (new_prg_list, output_remaining_body, new_prg_set)

    @classmethod
    def get_guard_domain(cls, cur_variable_dependencies, domain, guard, guard_string, variable_dependencies_aggregate, aggregate_dict):

        if guard_string in cur_variable_dependencies:
            # Guard is a Variable
            guard_domain = None

            operator = ComparisonTools.getCompOperator(guard.comparison)

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
            # Otherwise assuming int, will fail if e.g. is comparison or something else
            guard_domain = [int(str(guard.term))]
        return guard_domain

    @classmethod
    def rewriting_no_body_aggregate_strategy(cls, aggregate_index, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain, rule_positive_body):

        new_prg_list, output_remaining_body, new_prg_set = cls.rewriting_aggregate_strategy(aggregate_index, aggregate_dict, variables_dependencies_aggregate, aggregate_mode, cur_variable_dependencies, domain, rule_positive_body)

        return (new_prg_list, output_remaining_body, list(set(new_prg_set)))
