# pylint: disable=C0103
"""
Necessary for domain inference.
In conjunction with the Term-transformer used to infer the domain.
"""

import clingo
from clingo.ast import Transformer

from .comparison_tools import ComparisonTools


class DomainTransformer(Transformer):
    """
    Necessary for domain inference.
    In conjunction with the Term-transformer used to infer the domain.
    """

    def __init__(self, safe_variables_rules, domain, comparisons):
        self.safe_variables_rules = safe_variables_rules
        self.domain = domain
        self.comparisons = comparisons

        self.current_head = None
        self.variables_visited = {}

        self.current_function = None
        self.current_function_position = 0
        self.current_head_function = None
        self.current_head_functions = {}

        self.current_rule_position = 0

    def visit_Rule(self, node):
        """
        Visits an clingo-AST rule.
        """
        self.current_head = node.head

        head = node.head
        if hasattr(node.head, "atom") and hasattr(node.head.atom, "symbol"):
            head = node.head.atom.symbol
        self.current_head_functions[str(node.head)] = head

        self.visit_children(node)

        self.current_rule_position += 1
        self._reset_temporary_rule_variables()
        return node

    def visit_Function(self, node):
        """
        Visits an clingo-AST function.
        """
        self.current_function = node

        if str(self.current_function) == str(self.current_head):
            self.current_head_function = node

        self.visit_children(node)

        self._reset_temporary_function_variables()
        return node

    def visit_Aggregate(self, node):
        """
        Visits an clingo-AST aggregate.
        """
        if str(node) == str(self.current_head):
            for elem in node.elements:
                self.current_head_functions[
                    str(elem.literal)
                ] = elem.literal.atom.symbol  # is the function

        self.visit_children(node)

        return node

    def visit_Variable(self, node):
        """
        Visits an clingo-AST variable.
        Takes care of most things about domain-inference.
        """
        rule_is_in_safe_variables = (
            str(self.current_rule_position) in self.safe_variables_rules
        )

        if rule_is_in_safe_variables:
            self.variables_visited[str(node)] = 0

            if str(node) in self.safe_variables_rules[str(self.current_rule_position)]:
                safe_positions = self.safe_variables_rules[
                    str(self.current_rule_position)
                ][str(node)]

                self.remove_unnecessary_safe_positions(safe_positions)

                new_domain, all_variables_present = self._generate_new_domain(
                    safe_positions
                )

                new_domain = self.try_upper_bound_domain(
                    all_variables_present, node, new_domain
                )

                if all_variables_present is True:
                    variable_is_in_head = (
                        self.current_function
                        and str(self.current_function) in self.current_head_functions
                    )

                    new_position = self.current_function_position

                    if variable_is_in_head:
                        head = self.current_head_functions[str(self.current_function)]
                        new_name = head.name

                    rule_name = str(self.current_rule_position)
                    variable_name = str(node)
                    new_domain_variable_name = (
                        f"term_rule_{rule_name}_variable_{variable_name}"
                    )

                    for new_value in new_domain:
                        if variable_is_in_head:
                            self._add_symbolic_term_to_domain(
                                new_name, new_position, new_value
                            )

                        self._add_symbolic_term_to_domain(
                            new_domain_variable_name, "0", new_value
                        )

        if self.current_function:
            self.current_function_position += 1

        return node

    def _generate_new_domain(self, safe_positions):
        new_domain = None
        all_variables_present = True

        for safe_position in safe_positions:
            if safe_position["signum"] == 1:
                # ''not''
                continue

            if safe_position["type"] == "function":
                (
                    return_value,
                    all_variables_present,
                    new_domain,
                ) = self._generate_new_domain_function_helper(
                    safe_position, all_variables_present, new_domain
                )

                if return_value is False:
                    break

            elif safe_position["type"] == "term":
                (
                    new_domain,
                    all_variables_present,
                ) = self._generate_new_domain_term_helper(
                    safe_position, all_variables_present, new_domain
                )

            else:
                # not implemented
                assert False
        return new_domain, all_variables_present

    def _generate_new_domain_function_helper(
        self, safe_position, all_variables_present, new_domain
    ):
        safe_pos_name = safe_position["name"]
        safe_pos_position = safe_position["position"]

        if (
            safe_pos_name in self.domain
            and safe_pos_position in self.domain[safe_pos_name]
        ):
            cur_domain = set(self.domain[safe_pos_name][safe_pos_position])

            if new_domain:
                new_domain = new_domain.intersection(cur_domain)
            else:
                new_domain = cur_domain
        else:
            all_variables_present = False
            return (False, all_variables_present, new_domain)

        return (True, all_variables_present, new_domain)

    def _generate_new_domain_term_helper(
        self, safe_position, all_variables_present, new_domain
    ):
        rule_name = str(self.current_rule_position)

        variable_assignments = {}

        for variable in safe_position["variables"]:
            new_domain_variable_name = f"term_rule_{rule_name}_variable_{variable}"
            if new_domain_variable_name in self.domain:
                variable_assignments[variable] = self.domain[new_domain_variable_name][
                    "0"
                ]
            else:
                all_variables_present = False
                break

        if all_variables_present:
            new_domain = ComparisonTools.generate_domain(
                variable_assignments, safe_position["operation"]
            )

        return new_domain, all_variables_present

    def remove_unnecessary_safe_positions(self, safe_positions):
        """
        If a variable has a ''safe'' position that is a term, then the term-safe-position can be removed,
        if the variable has at least one more safe-position.
        """
        if len(safe_positions) > 1:
            for safe_position_index in range(
                len(safe_positions)
            ):  # Remove terms if len > 1
                safe_position = safe_positions[safe_position_index]

                if safe_position["type"] == "term":
                    del safe_positions[safe_position_index]

                safe_position_index -= 1

    def _add_symbolic_term_to_domain(self, identifier, position, value):
        """
        e.g. consider p(1,2).
        then one has to call this method twice:
        First Call:
            - p is the identifier
            - 0 is the position
            - 1 is the value
        Second Call:
            - p is the identifier
            - 1 is the position
            - 2 is the value
        """
        if str(identifier) not in self.domain:
            self.domain[str(identifier)] = {}

        if str(position) not in self.domain[str(identifier)]:
            self.domain[str(identifier)][str(position)] = []

        if str(value) not in self.domain[str(identifier)][str(position)]:
            self.domain[str(identifier)][str(position)].append(str(value))

        if "0_terms" not in self.domain:
            self.domain["0_terms"] = []

        if str(value) not in self.domain["0_terms"]:
            self.domain["0_terms"].append(str(value))

    def visit_SymbolicTerm(self, node):
        """
        Visits an clingo-AST symbolic term (constant).
        """
        if self.current_function:
            self.current_function_position += 1

        return node

    def _reset_temporary_rule_variables(self):
        self.current_head = None
        self.current_head_functions = {}
        self.variables_visited = {}

    def _reset_temporary_function_variables(self):
        self.current_function = None
        self.current_function_position = 0
        self.current_head_function = None

    def try_upper_bound_domain(self, all_variables_present, node, new_domain):
        """
        If there is a comparison like X < 5 one can (possibly) make the domain smaller.
        """

        if (
            all_variables_present
            and str(self.current_rule_position) in self.comparisons
            and str(node) in self.comparisons[str(self.current_rule_position)]
        ):
            comparisons = self.comparisons[str(self.current_rule_position)][str(node)]

            for comparison in comparisons:
                if len(comparison.guards) >= 2:
                    assert False  # Not implemented (only e.g. A = B implemented, not A = B = C)
                left = comparison.term
                right = comparison.guards[0].term
                comparison_operator = comparison.guards[0].comparison

                new_domain = self.try_upper_boun_left_side(
                    node, new_domain, left, right, comparison_operator
                )
                new_domain = self.try_upper_bound_right_side(
                    node, new_domain, left, right, comparison_operator
                )

        return new_domain

    def try_upper_bound_right_side(
        self, node, new_domain, left, right, comparison_operator
    ):
        """
        Check if right side can be upper-bounded.
        """
        if (
            str(node) == str(right)
            and str(left).isdigit()
            and (
                comparison_operator == int(clingo.ast.ComparisonOperator.GreaterThan)
                or comparison_operator
                == int(clingo.ast.ComparisonOperator.GreaterEqual)
            )
        ):
            new_domain = list(new_domain)

            new_domain_index = 0

            while new_domain_index < len(new_domain):
                domain_element = new_domain[new_domain_index]

                violates = False

                if comparison_operator == int(
                    clingo.ast.ComparisonOperator.GreaterEqual
                ):
                    if int(domain_element) > int(str(left)):
                        violates = True

                if comparison_operator == int(
                    clingo.ast.ComparisonOperator.GreaterThan
                ):
                    if int(domain_element) >= int(str(left)):
                        violates = True

                if violates:
                    del new_domain[new_domain_index]

                    new_domain_index -= 1

                new_domain_index += 1

            new_domain = set(new_domain)
        return new_domain

    def try_upper_boun_left_side(
        self, node, new_domain, left, right, comparison_operator
    ):
        """
        Check if left side can be upper-bounded.
        """
        if (
            str(node) == str(left)
            and str(right).isdigit()
            and (
                comparison_operator == int(clingo.ast.ComparisonOperator.LessThan)
                or comparison_operator == int(clingo.ast.ComparisonOperator.LessEqual)
            )
        ):
            new_domain = list(new_domain)

            new_domain_index = 0

            while new_domain_index < len(new_domain):
                domain_element = new_domain[new_domain_index]

                violates = False

                if comparison_operator == int(clingo.ast.ComparisonOperator.LessEqual):
                    if int(domain_element) > int(str(right)):
                        violates = True

                if comparison_operator == int(clingo.ast.ComparisonOperator.LessThan):
                    if int(domain_element) >= int(str(right)):
                        violates = True

                if violates:
                    del new_domain[new_domain_index]

                    new_domain_index -= 1

                new_domain_index += 1

            new_domain = set(new_domain)
        return new_domain
