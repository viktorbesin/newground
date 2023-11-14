# pylint: disable=W0102
"""
General helper module for the reduction.
"""

import networkx as nx


class HelperPart:
    """
    General helper class for the reduction.
    """

    @classmethod
    def get_domain_values_from_rule_variable(
        cls, rule, variable, domain, safe_variables_rules, rule_variables_predicates={}
    ):
        """
        Provided a rule number and a variable in that rule, one gets the domain of this variable.
        If applicable it automatically calculates the intersection of different domains.
        """

        if "0_terms" not in domain:
            # If no domain could be inferred
            raise Exception("A domain must exist when calling this method!")

        possible_domain_value_name = f"term_rule_{str(rule)}_variable_{str(variable)}"
        if possible_domain_value_name in domain:
            return domain[possible_domain_value_name]["0"]

        if len(rule_variables_predicates.keys()) > 0:
            if variable in rule_variables_predicates:
                respective_predicates = rule_variables_predicates[variable]
                total_domain = None

                total_domain = cls._get_variable_domain_from_occurrences(
                    domain, respective_predicates, total_domain
                )

                if total_domain is not None:
                    return list(total_domain)

        return cls._get_alternative_domain(safe_variables_rules, rule, domain, variable)

    @classmethod
    def _get_alternative_domain(cls, safe_variables_rules, rule, domain, variable):
        if str(rule) not in safe_variables_rules:
            return domain["0_terms"]

        if str(variable) not in safe_variables_rules[str(rule)]:
            return domain["0_terms"]

        total_domain = None

        for domain_type in safe_variables_rules[str(rule)][str(variable)]:
            if domain_type["type"] == "function":
                domain_name = domain_type["name"]
                domain_position = domain_type["position"]

                if domain_name not in domain:
                    return domain["0_terms"]

                if domain_position not in domain[domain_name]:
                    return domain["0_terms"]

                cur_domain = domain[domain_name][domain_position]

                if total_domain:
                    total_domain = total_domain.intersection(set(cur_domain))
                else:
                    total_domain = set(cur_domain)

        if total_domain is None:
            return domain["0_terms"]

        return list(total_domain)

    @classmethod
    def _get_variable_domain_from_occurrences(
        cls, domain, respective_predicates, total_domain
    ):
        for respective_predicate in respective_predicates:
            respective_predicate_name = respective_predicate[0].name
            respective_predicate_position = respective_predicate[1]

            if (
                respective_predicate_name not in domain
                or str(respective_predicate_position)
                not in domain[respective_predicate_name]
            ):
                continue

            cur_domain = domain[respective_predicate_name][
                str(respective_predicate_position)
            ]

            if total_domain:
                total_domain = total_domain.intersection(set(cur_domain))
            else:
                total_domain = set(cur_domain)
        return total_domain

    @classmethod
    def ignore_exception(cls, ignore_exception=Exception, default_value=None):
        """Decorator for ignoring exception from a function
        e.g.   @ignore_exception(DivideByZero)
        e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
        """

        def dec(function):
            def _dec(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except ignore_exception:
                    return default_value

            return _dec

        return dec

    @classmethod
    def generate_head_atom(
        cls,
        combination,
        h_vars,
        h_args,
        f_vars_needed,
        combination_associated_variables,
        current_rule_position,
    ):
        """
        Needed for foundedness checks.
        Generates the head atom of a foundedness-check-rule.
        """
        head_combination_list_2 = []
        head_combination = {}

        full_head_args = []

        if len(h_vars) > 0:
            not_head_counter, unfound_atom = cls._generate_head_atom_with_variables(
                combination,
                h_vars,
                h_args,
                f_vars_needed,
                combination_associated_variables,
                head_combination_list_2,
                head_combination,
                full_head_args,
                current_rule_position,
            )

        elif len(h_args) > 0 and len(h_vars) == 0:
            for h_arg in h_args:
                head_combination_list_2.append(h_arg)
                head_combination[h_arg] = h_arg
                full_head_args.append(h_arg)

            if (
                len(list(head_combination_list_2)) > 0
                and len(("".join(head_combination_list_2)).strip()) > 0
            ):
                unfound_atom = f"r{current_rule_position}_unfound({','.join(head_combination_list_2)})"
            else:
                unfound_atom = f"r{current_rule_position}_unfound_"

            not_head_counter = 0

        else:
            unfound_atom = f"r{current_rule_position}_unfound_"
            not_head_counter = 0

        return (
            head_combination,
            head_combination_list_2,
            unfound_atom,
            not_head_counter,
            full_head_args,
        )

    @classmethod
    def _generate_head_atom_with_variables(
        cls,
        combination,
        h_vars,
        h_args,
        f_vars_needed,
        combination_associated_variables,
        head_combination_list_2,
        head_combination,
        full_head_args,
        current_rule_position,
    ):
        head_counter = 0
        for h_arg in h_args:
            if h_arg in h_vars and h_arg in f_vars_needed:
                combination_variable_position = combination_associated_variables[h_arg]

                head_combination[h_arg] = combination[combination_variable_position]
                full_head_args.append(combination[combination_variable_position])

                if combination_variable_position > head_counter:
                    head_counter = combination_variable_position

            elif h_arg not in h_vars:
                head_combination[h_arg] = h_arg

                full_head_args.append(h_arg)
            else:
                full_head_args.append("_")

        for h_arg in h_args:
            if h_arg in head_combination:
                head_combination_list_2.append(head_combination[h_arg])

        if (
            len(head_combination_list_2) > 0
            and len(list(head_combination_list_2)) > 0
            and len(("".join(head_combination_list_2)).strip()) > 0
        ):
            unfound_atom = (
                f"r{current_rule_position}_unfound({','.join(head_combination_list_2)})"
            )
        else:
            unfound_atom = f"r{current_rule_position}_unfound_"

        not_head_counter = head_counter

        return not_head_counter, unfound_atom

    @classmethod
    def add_atom_to_unfoundedness_check(
        cls, head_string, unfound_atom, unfounded_rules, current_rule_position
    ):
        """
        Adds an atom to the ''unfoundedness-check'', i.e.,
        the check at the end of the program (that nothing is unfound).
        """
        if head_string not in unfounded_rules:
            unfounded_rules[head_string] = {}

        if str(current_rule_position) not in unfounded_rules[head_string]:
            unfounded_rules[head_string][str(current_rule_position)] = []

        unfounded_rules[head_string][str(current_rule_position)].append(unfound_atom)

    @classmethod
    def get_vars_needed(cls, h_vars, f_vars, f_rem, graph):
        """
        Needed for foundedness, gets the reachable variables from one variables.
        """
        f_vars_needed = [
            f for f in f_vars if f in h_vars
        ]  # bounded head vars which are needed for foundation
        for r in f_rem:
            for n in nx.dfs_postorder_nodes(graph, source=r):
                if n in h_vars and n not in f_vars_needed:
                    f_vars_needed.append(n)
        return f_vars_needed
