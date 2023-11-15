# pylint: disable=R0913
"""
General module for the rewriting strategy.
"""
from ..comparison_tools import ComparisonTools
from .rewriting_count_sum import RewritingCountSum
from .rewriting_min_max import RewritingMinMax


class RSRewriting:
    """
    General class for the rewriting strategy.
    """

    @classmethod
    def rewriting_aggregate_strategy(
        cls,
        aggregate_dict,
        variables_dependencies_aggregate,
        aggregate_mode,
        cur_variable_dependencies,
        domain,
        rule_positive_body,
    ):
        """
        Main caller method for the rewriting procedure.
        """
        str_type = aggregate_dict["function"][1]

        new_prg_list = []
        new_prg_set = []
        output_remaining_body = []

        if aggregate_dict["left_guard"]:
            cls.handle_left_guard(
                aggregate_dict,
                variables_dependencies_aggregate,
                aggregate_mode,
                cur_variable_dependencies,
                domain,
                rule_positive_body,
                str_type,
                new_prg_list,
                new_prg_set,
                output_remaining_body,
            )

        if aggregate_dict["right_guard"]:
            cls.handle_right_guard(
                aggregate_dict,
                variables_dependencies_aggregate,
                aggregate_mode,
                cur_variable_dependencies,
                domain,
                rule_positive_body,
                str_type,
                new_prg_list,
                new_prg_set,
                output_remaining_body,
            )

        return (new_prg_list, list(set(output_remaining_body)), list(set(new_prg_set)))

    @classmethod
    def handle_right_guard(
        cls,
        aggregate_dict,
        variables_dependencies_aggregate,
        aggregate_mode,
        cur_variable_dependencies,
        domain,
        rule_positive_body,
        str_type,
        new_prg_list,
        new_prg_set,
        output_remaining_body,
    ):
        """
        Method which handles the right guard of the aggregate.
        """
        right_guard = aggregate_dict["right_guard"]
        right_guard_string = str(right_guard.term)

        right_guard_domain = cls.get_guard_domain(
            cur_variable_dependencies,
            domain,
            right_guard,
            right_guard_string,
        )

        operator = ComparisonTools.get_comp_operator(right_guard.comparison)
        operator_type = operator

        string_capsulation = "right"

        (
            new_prg_list_tmp,
            output_remaining_body_tmp,
            new_prg_set_tmp,
        ) = cls.aggregate_caller(
            str_type,
            aggregate_dict,
            variables_dependencies_aggregate,
            aggregate_mode,
            cur_variable_dependencies,
            right_guard_domain,
            operator_type,
            string_capsulation,
            right_guard_string,
            rule_positive_body,
            domain,
        )

        new_prg_list += new_prg_list_tmp
        output_remaining_body += output_remaining_body_tmp
        new_prg_set += new_prg_set_tmp

    @classmethod
    def handle_left_guard(
        cls,
        aggregate_dict,
        variables_dependencies_aggregate,
        aggregate_mode,
        cur_variable_dependencies,
        domain,
        rule_positive_body,
        str_type,
        new_prg_list,
        new_prg_set,
        output_remaining_body,
    ):
        """
        Method which handles the left guard of the aggregate.
        """
        left_guard = aggregate_dict["left_guard"]
        left_guard_string = str(left_guard.term)

        left_guard_domain = cls.get_guard_domain(
            cur_variable_dependencies,
            domain,
            left_guard,
            left_guard_string,
        )

        operator = ComparisonTools.get_comp_operator(left_guard.comparison)

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

        (
            new_prg_list_tmp,
            output_remaining_body_tmp,
            new_prg_set_tmp,
        ) = cls.aggregate_caller(
            str_type,
            aggregate_dict,
            variables_dependencies_aggregate,
            aggregate_mode,
            cur_variable_dependencies,
            left_guard_domain,
            operator_type,
            string_capsulation,
            left_guard_string,
            rule_positive_body,
            domain,
        )

        new_prg_list += new_prg_list_tmp
        output_remaining_body += output_remaining_body_tmp
        new_prg_set += new_prg_set_tmp
        return left_guard_string

    @classmethod
    def aggregate_caller(
        cls,
        str_type,
        aggregate_dict,
        variables_dependencies_aggregate,
        aggregate_mode,
        cur_variable_dependencies,
        guard_domain,
        operator_type,
        string_capsulation,
        guard_string,
        rule_positive_body,
        domain,
    ):
        """
        Method which calls the Count/Sum OR Min/Max aggregate-sum-classes.
        """

        if str_type in ["count", "sum"]:
            (
                new_prg_list,
                output_remaining_body,
                new_prg_set,
            ) = RewritingCountSum.add_count_sum_aggregate_rules(
                aggregate_dict,
                variables_dependencies_aggregate,
                aggregate_mode,
                cur_variable_dependencies,
                guard_domain,
                operator_type,
                string_capsulation,
                guard_string,
                rule_positive_body,
                domain,
            )

        elif str_type in ["max", "min"]:
            (
                new_prg_list,
                output_remaining_body,
                new_prg_set,
            ) = RewritingMinMax.add_min_max_aggregate_rules(
                str_type,
                aggregate_dict,
                variables_dependencies_aggregate,
                aggregate_mode,
                guard_domain,
                operator_type,
                string_capsulation,
                guard_string,
                rule_positive_body,
            )

        else:
            raise Exception("NOT IMPLMENTED AGGREGATE TYPE: " + str_type)

        return (new_prg_list, output_remaining_body, new_prg_set)

    @classmethod
    def get_guard_domain(
        cls,
        cur_variable_dependencies,
        domain,
        guard,
        guard_string,
    ):
        """
        Method which gets the guard domain.
        """
        if guard_string in cur_variable_dependencies:
            # Guard is a Variable
            guard_domain = None

            ComparisonTools.get_comp_operator(guard.comparison)

            for var_dependency in cur_variable_dependencies[guard_string]:
                var_dependency_argument_position = -1
                var_dependency_argument_position_counter = 0
                for argument in var_dependency.arguments:
                    if str(argument) == guard_string:
                        var_dependency_argument_position = (
                            var_dependency_argument_position_counter
                        )
                        break

                    var_dependency_argument_position_counter += 1

                cur_var_dependency_domain = set(
                    domain[var_dependency.name][str(var_dependency_argument_position)]
                )

                if guard_domain is None:
                    guard_domain = cur_var_dependency_domain
                else:
                    guard_domain = set(guard_domain).intersection(
                        cur_var_dependency_domain
                    )

        else:
            # Otherwise assuming int, will fail if e.g. is comparison or something else
            guard_domain = [int(str(guard.term))]
        return guard_domain

    @classmethod
    def rewriting_no_body_aggregate_strategy(
        cls,
        aggregate_dict,
        variables_dependencies_aggregate,
        aggregate_mode,
        cur_variable_dependencies,
        domain,
        rule_positive_body,
    ):
        """
        Wrapper for rewriting Strategy for RS-PLUS.
        """
        (
            new_prg_list,
            output_remaining_body,
            new_prg_set,
        ) = cls.rewriting_aggregate_strategy(
            aggregate_dict,
            variables_dependencies_aggregate,
            aggregate_mode,
            cur_variable_dependencies,
            domain,
            rule_positive_body,
        )

        return (new_prg_list, output_remaining_body, list(set(new_prg_set)))
