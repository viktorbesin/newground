# pylint: disable=R0913
"""
Rewriting min-max aggregates.
"""

from .aggregate_mode import AggregateMode


class RewritingMinMax:
    """
    Class for rewriting-min-max aggregates.
    """

    @classmethod
    def add_min_max_aggregate_rules(
        cls,
        str_type,
        aggregate_dict,
        variable_dependencies,
        aggregate_mode,
        guard_domain,
        operator_type,
        string_capsulation,
        guard_string,
        rule_positive_body,
    ):
        """
        Add min-max aggregate rules.
        """
        new_prg_part_list = []
        new_prg_part_set = []

        str_type = aggregate_dict["function"][1]
        str_id = aggregate_dict["id"]

        number_of_elements = len(aggregate_dict["elements"])

        original_rule_additional_body_literals = []

        if (
            number_of_elements == 1
            and (operator_type in [">=", ">"])
            and len(list(guard_domain)) == 1
            and str_type == "max"
        ):
            # Handle special case RM (RM from paper, monotone agg., single element, single domain)
            original_rule_additional_body_literals += cls._handle_min_max_rm_case(
                aggregate_dict, guard_domain, operator_type
            )

        elif (
            number_of_elements == 1
            and (operator_type in ["<=", "<"])
            and len(list(guard_domain)) == 1
            and str_type == "min"
        ):
            # Handle special case RM (RM from paper, monotone agg., single element, single domain)
            original_rule_additional_body_literals += cls._handle_min_max_rm_case(
                aggregate_dict, guard_domain, operator_type
            )

        else:
            if len(list(guard_domain)) == 1:
                guard_value = int(str(list(guard_domain)[0]))  # Assuming constant

                cls._add_min_max_single_domain_adder(
                    aggregate_dict,
                    aggregate_mode,
                    str_type,
                    str_id,
                    variable_dependencies,
                    operator_type,
                    string_capsulation,
                    guard_value,
                    original_rule_additional_body_literals,
                    new_prg_part_list,
                    new_prg_part_set,
                    [],
                    guard_string,
                    rule_positive_body,
                )

            else:
                guard_domain_list = [int(value) for value in list(guard_domain)]

                for guard_value in guard_domain_list:
                    always_add_variable_dependecies = [str(guard_value)]

                    cls._add_min_max_single_domain_adder(
                        aggregate_dict,
                        aggregate_mode,
                        str_type,
                        str_id,
                        variable_dependencies,
                        operator_type,
                        string_capsulation,
                        guard_value,
                        original_rule_additional_body_literals,
                        new_prg_part_list,
                        new_prg_part_set,
                        always_add_variable_dependecies,
                        guard_string,
                        rule_positive_body,
                    )

        return (
            new_prg_part_list,
            original_rule_additional_body_literals,
            list(set(new_prg_part_set)),
        )
        # new_prg_list, output_remaining_body, new_prg_set

    @classmethod
    def _handle_min_max_rm_case(cls, aggregate_dict, guard_domain, operator_type):
        element = aggregate_dict["elements"][0]
        terms = element["terms"]
        conditions = element["condition_ast"]

        guard_value = int(list(guard_domain)[0])
        new_body_list = []

        compare_variable = terms[0]

        # Add existing conditions
        for condition in conditions:
            new_body_list.append(str(condition))

        # Add new literal
        new_body_list.append(f"{compare_variable} {operator_type} {guard_value}")

        return new_body_list

    @classmethod
    def _add_min_max_single_domain_adder(
        cls,
        aggregate,
        aggregate_mode,
        str_type,
        str_id,
        variable_dependencies,
        operator_type,
        string_capsulation,
        guard_value,
        original_rule_additional_body_literals,
        new_prg_part_list,
        new_prg_part_set,
        always_add_variable_dependecies,
        guard_string,
        rule_positive_body,
    ):
        elements = aggregate["elements"]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"]

        element_predicate_names = []

        # Define common head:
        head_name = f"{str_type}_ag{str_id}_{string_capsulation}"
        if len(variable_dependencies + always_add_variable_dependecies) == 0:
            head_terms_string = "(1)"
        else:
            head_terms_string = (
                f"({','.join(variable_dependencies + always_add_variable_dependecies)})"
            )
        head = f"{head_name}{head_terms_string}"

        if len(rule_positive_body) > 0:
            positive_body_string = (
                ",".join([str(node) for node in rule_positive_body]) + ","
            )
        else:
            positive_body_string = ""

        # For each element:
        for element_index in range(len(elements)):
            cls._single_element_min_max_handler(
                aggregate_mode,
                str_type,
                str_id,
                variable_dependencies,
                operator_type,
                guard_value,
                new_prg_part_list,
                new_prg_part_set,
                always_add_variable_dependecies,
                elements,
                element_predicate_names,
                head_name,
                head_terms_string,
                head,
                positive_body_string,
                element_index,
            )

        cls._rewrite_original_rule(
            str_type,
            variable_dependencies,
            operator_type,
            original_rule_additional_body_literals,
            new_prg_part_list,
            always_add_variable_dependecies,
            guard_string,
            head_name,
        )

    @classmethod
    def _single_element_min_max_handler(
        cls,
        aggregate_mode,
        str_type,
        str_id,
        variable_dependencies,
        operator_type,
        guard_value,
        new_prg_part_list,
        new_prg_part_set,
        always_add_variable_dependecies,
        elements,
        element_predicate_names,
        head_name,
        head_terms_string,
        head,
        positive_body_string,
        element_index,
    ):
        element = elements[element_index]

        conditions_string = ",".join([str(node) for node in element["condition_ast"]])

        terms = element["terms"]
        element_dependent_variables = []

        for variable in element["condition_variables"]:
            if variable in variable_dependencies:
                element_dependent_variables.append(variable)

        tuple_predicate_head = None
        if aggregate_mode in [AggregateMode.RS_STAR, AggregateMode.RS]:
            element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"

            terms_string = f"{','.join(terms + element_dependent_variables + always_add_variable_dependecies)}"

            tuple_predicate_head = f"{element_predicate_name}({terms_string})"
            tuple_predicate_rule = f"{tuple_predicate_head} :- {conditions_string}."

            new_prg_part_set.append(tuple_predicate_rule)
            element_predicate_names.append(element_predicate_name)

        if str_type == "max":
            cls._max_aggregate(
                aggregate_mode,
                operator_type,
                guard_value,
                new_prg_part_list,
                head_name,
                head_terms_string,
                head,
                positive_body_string,
                conditions_string,
                terms,
                tuple_predicate_head,
            )

        elif str_type == "min":
            cls._min_aggregate(
                aggregate_mode,
                operator_type,
                guard_value,
                new_prg_part_list,
                head_name,
                head_terms_string,
                head,
                positive_body_string,
                conditions_string,
                terms,
                tuple_predicate_head,
            )

    @classmethod
    def _rewrite_original_rule(
        cls,
        str_type,
        variable_dependencies,
        operator_type,
        original_rule_additional_body_literals,
        new_prg_part_list,
        always_add_variable_dependecies,
        guard_string,
        head_name,
    ):
        if len(variable_dependencies + always_add_variable_dependecies) == 0:
            original_rule_head_terms_string = "(1)"
        else:
            if len(always_add_variable_dependecies) == 0:
                original_rule_head_terms_string = f"({','.join(variable_dependencies)})"
            else:
                original_rule_head_terms_string = (
                    f"({','.join(variable_dependencies + [guard_string])})"
                )

        head = f"{head_name}{original_rule_head_terms_string}"
        if str_type == "max" and operator_type in [">", ">="]:
            original_rule_additional_body_literals.append(head)

        elif str_type == "max" and operator_type in ["<", "<="]:
            original_rule_additional_body_literals.append(f"not {head}")

        elif str_type == "min" and operator_type in ["<", "<="]:
            original_rule_additional_body_literals.append(head)

        elif str_type == "min" and operator_type in [">", ">="]:
            original_rule_additional_body_literals.append(f"not {head}")

        elif operator_type == "=":
            original_rule_additional_body_literals.append(
                f"{head_name}_1{original_rule_head_terms_string}"
            )
            original_rule_additional_body_literals.append(
                f"not {head_name}_2{original_rule_head_terms_string}"
            )

        elif operator_type == "!=":
            intermediate_rule = (
                f"not_{head} :- {head_name}_1{original_rule_head_terms_string}, "
                + f"not {head_name}_2{original_rule_head_terms_string}."
            )
            new_prg_part_list.append(intermediate_rule)

            original_rule_additional_body_literals.append(f"not not_{head}")

        else:
            raise Exception("Not Implemented")

    @classmethod
    def _min_aggregate(
        cls,
        aggregate_mode,
        operator_type,
        guard_value,
        new_prg_part_list,
        head_name,
        head_terms_string,
        head,
        positive_body_string,
        conditions_string,
        terms,
        tuple_predicate_head,
    ):
        if operator_type in [">=", "<=", ">", "<"]:
            if operator_type == ">=":
                final_guard_value = guard_value - 1
            elif operator_type == ">":
                final_guard_value = guard_value
            elif operator_type == "<=":
                final_guard_value = guard_value
            elif operator_type == "<":
                final_guard_value = guard_value - 1

            if aggregate_mode in [AggregateMode.RS_STAR, AggregateMode.RS]:
                rule_string = (
                    f"{head} :- {positive_body_string} {tuple_predicate_head}, "
                    + f"{terms[0]} <= {final_guard_value}."
                )
            elif aggregate_mode == AggregateMode.RS_PLUS:
                rule_string = (
                    f"{head} :- {positive_body_string} {conditions_string}, "
                    + f"{terms[0]} <= {final_guard_value}."
                )

            new_prg_part_list.append(rule_string)

        elif operator_type in ["!=", "="]:
            final_guard_value_1 = guard_value
            final_guard_value_2 = guard_value - 1

            if aggregate_mode in [AggregateMode.RS_STAR, AggregateMode.RS]:
                rule_string_1 = (
                    f"{head_name}_1{head_terms_string} :- {positive_body_string} "
                    + f"{tuple_predicate_head}, {terms[0]} <= {final_guard_value_1}."
                )
                rule_string_2 = (
                    f"{head_name}_2{head_terms_string} :- {positive_body_string} "
                    + f"{tuple_predicate_head}, {terms[0]} <= {final_guard_value_2}."
                )
            elif aggregate_mode == AggregateMode.RS_PLUS:
                rule_string_1 = (
                    f"{head_name}_1{head_terms_string} :- {positive_body_string} "
                    + f"{conditions_string}, {terms[0]} <= {final_guard_value_1}."
                )
                rule_string_2 = (
                    f"{head_name}_2{head_terms_string} :- {positive_body_string} "
                    + f"{conditions_string}, {terms[0]} <= {final_guard_value_2}."
                )

            new_prg_part_list.append(rule_string_1)
            new_prg_part_list.append(rule_string_2)
        else:
            raise Exception("Operator type '" + operator_type + "' not found!")

    @classmethod
    def _max_aggregate(
        cls,
        aggregate_mode,
        operator_type,
        guard_value,
        new_prg_part_list,
        head_name,
        head_terms_string,
        head,
        positive_body_string,
        conditions_string,
        terms,
        tuple_predicate_head,
    ):
        if operator_type in [">=", "<=", ">", "<"]:
            if operator_type == ">=":
                final_guard_value = guard_value
            elif operator_type == ">":
                final_guard_value = guard_value + 1
            elif operator_type == "<=":
                final_guard_value = guard_value + 1
            elif operator_type == "<":
                final_guard_value = guard_value

            if aggregate_mode in [AggregateMode.RS_STAR, AggregateMode.RS]:
                rule_string = (
                    f"{head} :- {positive_body_string} "
                    + f"{tuple_predicate_head}, {terms[0]} >= {final_guard_value}."
                )
            elif aggregate_mode == AggregateMode.RS_PLUS:
                rule_string = (
                    f"{head} :- {positive_body_string} "
                    + f"{conditions_string}, {terms[0]} >= {final_guard_value}."
                )

            new_prg_part_list.append(rule_string)

        elif operator_type in ["!=", "="]:
            final_guard_value_1 = guard_value
            final_guard_value_2 = guard_value + 1

            if aggregate_mode in [AggregateMode.RS_STAR, AggregateMode.RS]:
                rule_string_1 = (
                    f"{head_name}_1{head_terms_string} :- "
                    + f"{positive_body_string} {tuple_predicate_head}, "
                    + f"{terms[0]} >= {final_guard_value_1}."
                )
                rule_string_2 = (
                    f"{head_name}_2{head_terms_string} :- "
                    + f"{positive_body_string} {tuple_predicate_head}, "
                    + f"{terms[0]} >= {final_guard_value_2}."
                )

            elif aggregate_mode == AggregateMode.RS_PLUS:
                rule_string_1 = (
                    f"{head_name}_1{head_terms_string} :- "
                    + f"{positive_body_string} {conditions_string}, {terms[0]} >= {final_guard_value_1}."
                )
                rule_string_2 = (
                    f"{head_name}_2{head_terms_string} :- "
                    + f"{positive_body_string} {conditions_string}, {terms[0]} >= {final_guard_value_2}."
                )

            new_prg_part_list.append(rule_string_1)
            new_prg_part_list.append(rule_string_2)
        else:
            raise Exception("Operator type '" + operator_type + "' not found!")
