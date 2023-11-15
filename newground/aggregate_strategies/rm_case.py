"""
Module which handles the RM-Case.
"""
import clingo

from ..comparison_tools import ComparisonTools
from .count_aggregate_helper import CountAggregateHelper


class RMCase:
    """
    Class which handles the RM-Case.
    """

    @classmethod
    def handle_rm_case(
        cls,
        aggregate_dict,
        variable_dependencies,
        guard_domain,
        operator_type,
    ):
        """
        Method which handles the RM-Case.
        """
        element = aggregate_dict["elements"][0]

        all_diff_list_terms = []

        terms = element["terms"]

        conditions = element["condition_ast"]

        upper = int(list(guard_domain)[0])
        if operator_type == ">":
            upper += 1

        new_body_list = []

        for index in range(upper):
            cur_term_list = []
            for term in terms:
                if term in variable_dependencies:
                    cur_term_list.append(term)
                else:
                    cur_term_list.append(term + "_" + str(index))
            all_diff_list_terms.append(cur_term_list)

            for condition in conditions:
                cls._for_each_condition(
                    variable_dependencies, new_body_list, index, condition
                )

        all_diff_list = CountAggregateHelper.all_diff_generator(
            all_diff_list_terms, upper
        )

        new_body_list += all_diff_list

        return new_body_list

    @classmethod
    def _for_each_condition(
        cls, variable_dependencies, new_body_list, index, condition
    ):
        if (
            hasattr(condition, "atom")
            and hasattr(condition.atom, "symbol")
            and condition.atom.symbol.ast_type == clingo.ast.ASTType.Function
        ):
            cls._handle_function(variable_dependencies, new_body_list, index, condition)

        elif (
            hasattr(condition, "atom")
            and condition.atom.ast_type == clingo.ast.ASTType.Comparison
        ):
            cls._handle_comparison(
                variable_dependencies, new_body_list, index, condition
            )

    @classmethod
    def _handle_comparison(cls, variable_dependencies, new_body_list, index, condition):
        cur_comparison = condition.atom

        left = cur_comparison.term
        assert len(cur_comparison.guards) <= 1
        right = cur_comparison.guards[0].term

        arguments = ComparisonTools.get_arguments_from_operation(
            left
        ) + ComparisonTools.get_arguments_from_operation(right)

        arg_dict = {}

        for argument in arguments:
            if str(argument) in variable_dependencies:
                arg_dict[str(argument)] = str(argument)
            else:
                arg_dict[str(argument)] = str(argument) + "_" + str(index)

        new_left = ComparisonTools.instantiate_operation(left, arg_dict)
        new_right = ComparisonTools.instantiate_operation(right, arg_dict)
        new_comparison = ComparisonTools.comparison_handlings(
            cur_comparison.guards[0].comparison, new_left, new_right
        )

        new_body_list.append(new_comparison)

    @classmethod
    def _handle_function(cls, variable_dependencies, new_body_list, index, condition):
        cur_condition = condition.atom.symbol

        arg_list = []

        for argument in cur_condition.arguments:
            if str(argument) in variable_dependencies:
                arg_list.append(str(argument))
            else:
                arg_list.append(str(argument) + "_" + str(index))

        new_function = cur_condition.name + "(" + ",".join(arg_list) + ")"

        new_body_list.append(new_function)
