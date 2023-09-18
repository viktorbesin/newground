from .rm_case import RMCase
from .aggregate_mode import AggregateMode
from .rs_helper import RSHelper
from .rs_plus_star_helper import RSPlusStarHelper


class RSCount:

    @classmethod
    def _add_count_aggregate_rules(cls, aggregate_dict, variable_dependencies, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type, string_capsulation, guard_string, rule_positive_body, domain):

        new_prg_part_list = []
        new_prg_part_set = []

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"] 
        
        number_of_elements = len(aggregate_dict["elements"])

        original_rule_additional_body_literals = []

        if number_of_elements == 1 and (operator_type == ">=" or operator_type == ">") and len(list(guard_domain)) == 1:
            # Handle special case RM (RM from paper)
            original_rule_additional_body_literals += RMCase._handle_rm_case(aggregate_dict, variable_dependencies, aggregate_mode, cur_variable_dependencies, guard_domain, operator_type)

        else:
            if len(list(guard_domain)) == 1:
                guard_value = int(str(list(guard_domain)[0])) # Assuming constant

                cls._count_single_domain_adder(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, [], guard_string, rule_positive_body, domain)
            else:
                guard_domain_list = [int(value) for value in list(guard_domain)]

                for guard_value in guard_domain_list:
                    always_add_variable_dependecies = [str(guard_value)]

                    cls._count_single_domain_adder(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, always_add_variable_dependecies, guard_string, rule_positive_body, domain)

        return (new_prg_part_list, original_rule_additional_body_literals, list(set(new_prg_part_set)))

    @classmethod
    def _count_single_domain_adder(cls, aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, string_capsulation, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, new_prg_part_list, new_prg_part_set, always_add_variable_dependencies, guard_string, rule_positive_body, domain):

        skolem_constants = []
        if aggregate_mode == AggregateMode.RS:
            skolem_constants = RSHelper.generate_skolem_constants(aggregate_dict, domain)
            RSHelper.add_rs_tuple_predicate_rules(aggregate_dict, str_type, str_id, variable_dependencies, new_prg_part_set, always_add_variable_dependencies, rule_positive_body, skolem_constants)
        elif aggregate_mode == AggregateMode.RS_STAR:
            RSPlusStarHelper.add_rs_star_tuple_predicate_rules(aggregate_dict, str_type, str_id, variable_dependencies, new_prg_part_set, always_add_variable_dependencies)
        elif aggregate_mode == AggregateMode.RS_PLUS:
            pass
        else:
            print("NOT IMPLEMENTED")
            assert(False)

        count = guard_value
        count_predicate_name = f"{str_type}_ag{str_id}_{string_capsulation}"

        if operator_type in [">=",">","<=","<"]:
            rules_strings = cls.monotone_antimonotone_operators(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, cur_variable_dependencies, original_rule_additional_body_literals, always_add_variable_dependencies, guard_string, skolem_constants, count, count_predicate_name)

        elif operator_type == "!=":
            rules_strings = cls.not_equal_operator(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, always_add_variable_dependencies, guard_string, skolem_constants, count, count_predicate_name)

        elif operator_type == "=":
            rules_strings = cls.equal_operator(aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, cur_variable_dependencies, original_rule_additional_body_literals, always_add_variable_dependencies, guard_string, skolem_constants, count, count_predicate_name)

        else:
            print(f"Operator Type {operator_type} currently not supported!")
            raise Exception("Not supported operator type for aggregate!")

        for rule_string in rules_strings:
            new_prg_part_list.append(rule_string)

    @classmethod
    def equal_operator(cls, aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, cur_variable_dependencies, original_rule_additional_body_literals, always_add_variable_dependencies, guard_string, skolem_constants, count, count_predicate_name):
        if len(always_add_variable_dependencies) == 0:
            arguments = ""
            if len(variable_dependencies) == 0:
                arguments += "(1)"
            else:
                arguments += f"({','.join(variable_dependencies)})" 
        else:
                # Special case if guard is variable
            arguments = f"({','.join(variable_dependencies + [str(guard_string)])})" 

        if aggregate_mode == AggregateMode.RS: 
            original_rule_additional_body_literals.append(f"{count_predicate_name}_1{arguments}")
            original_rule_additional_body_literals.append(f"not {count_predicate_name}_2{arguments}")
        elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
            original_rule_additional_body_literals.append(f"not not_{count_predicate_name}_1{arguments}")
            original_rule_additional_body_literals.append(f"not not not_{count_predicate_name}_2{arguments}")

        count1 = count
        count2 = count + 1

        if aggregate_mode == AggregateMode.RS:
            rules_strings = RSHelper._rs_count_generate_count_rule(count_predicate_name + "_1", count1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies, skolem_constants)
            rules_strings += RSHelper._rs_count_generate_count_rule(count_predicate_name + "_2", count2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies, skolem_constants)
        elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
            rules_strings = RSPlusStarHelper._rs_plus_star_count_generate_bodies_and_helper_bodies(count_predicate_name + "_1", count1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)
            rules_strings += RSPlusStarHelper._rs_plus_star_count_generate_bodies_and_helper_bodies(count_predicate_name + "_2", count2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

        return rules_strings

    @classmethod
    def not_equal_operator(cls, aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, guard_value, cur_variable_dependencies, original_rule_additional_body_literals, always_add_variable_dependencies, guard_string, skolem_constants, count, count_predicate_name):
        if len(always_add_variable_dependencies) == 0:
            arguments = ""
            if len(variable_dependencies) == 0:
                arguments += "(1)"
            else:
                arguments += f"({','.join(variable_dependencies)})" 
        else:
                # Special case if guard is variable
            arguments = f"({','.join(variable_dependencies + [guard_string])})" 

        double_negated_count_predicate = f"not not_{count_predicate_name}{arguments}"
        original_rule_additional_body_literals.append(double_negated_count_predicate)

        count1 = count
        count2 = count + 1

        if aggregate_mode == AggregateMode.RS:
            rules_strings = RSHelper._rs_count_generate_count_rule(count_predicate_name + "_1", count1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies, skolem_constants)
            rules_strings += RSHelper._rs_count_generate_count_rule(count_predicate_name + "_2", count2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies, skolem_constants)
        elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
            rules_strings = RSPlusStarHelper._rs_plus_star_count_generate_bodies_and_helper_bodies(count_predicate_name + "_1", count1, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)
            rules_strings += RSPlusStarHelper._rs_plus_star_count_generate_bodies_and_helper_bodies(count_predicate_name + "_2", count2, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

        if len(always_add_variable_dependencies) == 0:
            arguments = ""
            if len(variable_dependencies) == 0:
                arguments += "(1)"
            else:
                arguments += f"({','.join(variable_dependencies)})" 
        else:
                # Special case if guard is variable
            arguments = f"({','.join(variable_dependencies + [str(guard_value)])})" 

        if aggregate_mode == AggregateMode.RS:
            intermediate_rule = f"not_{count_predicate_name}{arguments} :- {count_predicate_name}_1{arguments}, not {count_predicate_name}_2{arguments}."
        elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
            intermediate_rule = f"not_{count_predicate_name}{arguments} :- not not_{count_predicate_name}_1{arguments}, not_{count_predicate_name}_2{arguments}."

        rules_strings.append(intermediate_rule)

        return rules_strings

    @classmethod
    def monotone_antimonotone_operators(cls, aggregate_dict, aggregate_mode, str_type, str_id, variable_dependencies, operator_type, cur_variable_dependencies, original_rule_additional_body_literals, always_add_variable_dependencies, guard_string, skolem_constants, count, count_predicate_name):
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
            if aggregate_mode == AggregateMode.RS:
                double_negated_count_predicate = f"{count_predicate_name}{arguments}"
                original_rule_additional_body_literals.append(double_negated_count_predicate)
            elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
                double_negated_count_predicate = f"not not_{count_predicate_name}{arguments}"
                original_rule_additional_body_literals.append(double_negated_count_predicate)
        elif operator_type == "<=" or operator_type == "<":
            # Anti-Monotone
            if aggregate_mode == AggregateMode.RS:
                triple_negated_count_predicate = f"not {count_predicate_name}{arguments}"
                original_rule_additional_body_literals.append(triple_negated_count_predicate)
            elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
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

        if aggregate_mode == AggregateMode.RS:
            rules_strings = RSHelper._rs_count_generate_count_rule(count_predicate_name, count, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies, skolem_constants)
        elif aggregate_mode in [AggregateMode.RS_PLUS, AggregateMode.RS_STAR]:
            rules_strings = RSPlusStarHelper._rs_plus_star_count_generate_bodies_and_helper_bodies(count_predicate_name, count, aggregate_dict["elements"], str_type, str_id, variable_dependencies, aggregate_mode, cur_variable_dependencies, always_add_variable_dependencies)

        return rules_strings

