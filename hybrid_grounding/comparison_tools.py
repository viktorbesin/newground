# pylint: disable=R1705,W0108
"""
The comparison tools module is used as a helper module,
for various parts of the transformer.
It is useful for domain inference, instantiations, calculations, etc.
"""

import clingo


class ComparisonTools:
    """
    The comparison tools module is used as a helper module,
    for various parts of the transformer.
    It is useful for domain inference, instantiations, calculations, etc.
    """

    @classmethod
    def get_comp_operator(cls, comp):
        """
        @comp - The AST representation of the comparison operator.
        returns the string representation (or false, if not implemented).
        """
        if comp is int(clingo.ast.ComparisonOperator.Equal):
            return "="
        elif comp is int(clingo.ast.ComparisonOperator.NotEqual):
            return "!="
        elif comp is int(clingo.ast.ComparisonOperator.GreaterEqual):
            return ">="
        elif comp is int(clingo.ast.ComparisonOperator.GreaterThan):
            return ">"
        elif comp is int(clingo.ast.ComparisonOperator.LessEqual):
            return "<="
        elif comp is int(clingo.ast.ComparisonOperator.LessThan):
            return "<"

        assert False  # not implemented

    @classmethod
    def comparison_handlings(cls, comp, c1, c2):
        """
        @comp - The AST representation of the comparison operator.
        @c1 - The left side of the comparison (AST).
        @c2 - The right side of the comparison (AST).
        returns a string representation of the comparison operation (or false if not implemented).
        """
        if comp is int(clingo.ast.ComparisonOperator.Equal):
            return f"{c1} = {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.NotEqual):
            return f"{c1} != {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.GreaterEqual):
            return f"{c1} >= {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.GreaterThan):
            return f"{c1} > {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.LessEqual):
            return f"{c1} <= {c2}"
        elif comp is int(clingo.ast.ComparisonOperator.LessThan):
            return f"{c1} < {c2}"

        assert False  # not implemented

    @classmethod
    def compare_terms(cls, comp, c1, c2):
        """
        @comp - The AST representation of the comparison operator.
        @c1 - The left side of the comparison (Python-value - assumed int).
        @c2 - The right side of the comparison (Python-value - assumed int):
        returns the computed boolean value of the comparison.
        """
        if comp is int(clingo.ast.ComparisonOperator.Equal):  # == 5
            return c1 == c2
        elif comp is int(clingo.ast.ComparisonOperator.NotEqual):
            return c1 != c2
        elif comp is int(clingo.ast.ComparisonOperator.GreaterEqual):
            return c1 >= c2
        elif comp is int(clingo.ast.ComparisonOperator.GreaterThan):
            return c1 > c2
        elif comp is int(clingo.ast.ComparisonOperator.LessEqual):
            return c1 <= c2
        elif comp is int(clingo.ast.ComparisonOperator.LessThan):
            return c1 < c2

        assert False  # not implemented

    @classmethod
    def get_arguments_from_operation(cls, root):
        """
        @root - A AST operation/term.
        Given a root ast term, it computes all arguments from an operation.
        Performs a tree traversal of an operation (e.g. X+Y -> first ''+'', then ''X'' and lastly ''Y''
            -> then combines together)
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            return cls.get_arguments_from_operation(
                root.left
            ) + cls.get_arguments_from_operation(root.right)

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            return cls.get_arguments_from_operation(root.argument)

        elif (
            root.ast_type is clingo.ast.ASTType.Variable
            or root.ast_type is clingo.ast.ASTType.SymbolicTerm
        ):
            return [root]
        elif root.ast_type is clingo.ast.ASTType.Function:
            argument_list = []

            for argument in root.arguments:
                argument_list += cls.get_arguments_from_operation(argument)

            return argument_list

        assert False  # not implemented

    @classmethod
    def instantiate_operation(cls, root, variable_assignments):
        """
        @root - An AST operation/term.
        @variable_assignment - A variable-value dict.
        Instantiates a operation and returns the corresponding string.
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            string_rep = cls._get_binary_operator_type_as_string(root.operator_type)

            return (
                "("
                + cls.instantiate_operation(root.left, variable_assignments)
                + string_rep
                + cls.instantiate_operation(root.right, variable_assignments)
                + ")"
            )

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            string_rep = cls._get_unary_operator_type_as_string(root.operator_type)

            if string_rep != "ABSOLUTE":
                return (
                    "("
                    + string_rep
                    + cls.instantiate_operation(root.argument, variable_assignments)
                    + ")"
                )
            elif string_rep == "ABSOLUTE":
                return (
                    "(|"
                    + cls.instantiate_operation(root.argument, variable_assignments)
                    + "|)"
                )

        elif root.ast_type is clingo.ast.ASTType.Variable:
            variable_string = str(root)
            return variable_assignments[variable_string]

        elif root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return str(root)

        elif root.ast_type is clingo.ast.ASTType.Function:
            instantiations = []
            for argument in root.arguments:
                instantiations.append(
                    cls.instantiate_operation(argument, variable_assignments)
                )

            return f"{root.name}({','.join(instantiations)})"

        assert False  # not implemented

    @classmethod
    def _get_unary_operator_type_as_string(cls, operator_type):
        if operator_type == int(clingo.ast.UnaryOperator.Minus):
            return "-"
        elif operator_type == int(clingo.ast.UnaryOperator.Negation):
            return "~"
        elif operator_type == int(
            clingo.ast.UnaryOperator.Absolute
        ):  # Absolute, i.e. |X| needs special handling
            return "ABSOLUTE"

        print(
            f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!"
        )
        assert False  # not implemented

    @classmethod
    def _get_binary_operator_type_as_string(cls, operator_type):
        if operator_type == int(clingo.ast.BinaryOperator.XOr):
            return "^"
        elif operator_type == int(clingo.ast.BinaryOperator.Or):
            return "?"
        elif operator_type == int(clingo.ast.BinaryOperator.And):
            return "&"
        elif operator_type == int(clingo.ast.BinaryOperator.Plus):
            return "+"
        elif operator_type == int(clingo.ast.BinaryOperator.Minus):
            return "-"
        elif operator_type == int(clingo.ast.BinaryOperator.Multiplication):
            return "*"
        elif operator_type == int(clingo.ast.BinaryOperator.Division):
            return "/"
        elif operator_type == int(clingo.ast.BinaryOperator.Modulo):
            return "\\"
        elif operator_type == int(clingo.ast.BinaryOperator.Power):
            return "**"

        print(
            f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!"
        )
        assert False  # not implemented

    @classmethod
    def generate_domain(cls, variable_assignments, operation):
        """
        variable_assignments, corresponds to the domains of the variables,
        and operation is the actual comparison operation.

        If a variable is inducing in a comparison,
        this method creates its domain.
        """
        if operation.ast_type == clingo.ast.ASTType.SymbolicAtom:
            return [str(operation.symbol)]
        elif operation.ast_type == clingo.ast.ASTType.SymbolicTerm:
            return [str(operation.symbol)]
        elif operation.ast_type == clingo.ast.ASTType.Variable:
            return variable_assignments[str(operation.name)]
        elif operation.ast_type == clingo.ast.ASTType.UnaryOperation:
            return cls.generate_unary_operator_domain(
                operation.operator_type,
                cls.generate_domain(variable_assignments, operation.argument),
            )
        elif operation.ast_type == clingo.ast.ASTType.BinaryOperation:
            return cls.generate_binary_operator_domain(
                operation.operator_type,
                cls.generate_domain(variable_assignments, operation.left),
                cls.generate_domain(variable_assignments, operation.right),
            )

        print(operation)
        print(operation.ast_type)
        assert False

    @classmethod
    def generate_unary_operator_domain(cls, operator_type, domain):
        """
        @operator_type - AST type of unary-operator.
        @domain - the domain dict.
        Computes the resulting domain, of the operation.
        """
        if operator_type == int(clingo.ast.UnaryOperator.Minus):
            return cls.apply_unary_operation(domain, lambda d: -d)
        elif operator_type == int(clingo.ast.UnaryOperator.Negation):
            return cls.apply_unary_operation(domain, lambda d: ~d)
        elif operator_type == int(clingo.ast.UnaryOperator.Absolute):
            return cls.apply_unary_operation(domain, lambda d: abs(d))

        print(
            f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!"
        )
        assert False  # not implemented

    @classmethod
    def generate_binary_operator_domain(cls, operator_type, left_domain, right_domain):
        """
        @operator_type - AST type of binary-operator.
        @left_domain - Domain of the left part of the binary-operation.
        @right_domain - Domain of the right part of the binary operation.
        Computes the resulting domain, of the operation.
        """
        if operator_type == int(clingo.ast.BinaryOperator.XOr):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l ^ r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Or):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l | r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.And):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l & r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Plus):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l + r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Minus):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l - r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Multiplication):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l * r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Division):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l / r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Modulo):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: l % r
            )
        elif operator_type == int(clingo.ast.BinaryOperator.Power):
            return cls.apply_binary_operation(
                left_domain, right_domain, lambda l, r: pow(l, r)
            )

        print(
            f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!"
        )
        assert False  # not implemented

    @classmethod
    def evaluate_binary_operation(cls, operator_type, left_value, right_value):
        """
        @operator_type - AST operator type.
        @left_value - Python value (int).
        @right_value - Python value (int).
        Computes the resulting value after applying the operation.
        """
        if operator_type == int(clingo.ast.BinaryOperator.XOr):
            return int(left_value) ^ int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Or):
            return int(left_value) | int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.And):
            return int(left_value) & int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Plus):
            return int(left_value) + int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Minus):
            return int(left_value) - int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Multiplication):
            return int(left_value) * int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Division):
            return int(left_value) / int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Modulo):
            return int(left_value) % int(right_value)
        elif operator_type == int(clingo.ast.BinaryOperator.Power):
            return pow(int(left_value), int(right_value))

        print(
            f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!"
        )
        assert False  # not implemented

    @classmethod
    def evaluate_operation(cls, operation, variable_assignments):
        """
        @operation - AST operation.
        @variable_assignment - Variable assignment dict.
        Computes a tree-traversal and the resulting value of the whole operation.
        """
        if operation.ast_type == clingo.ast.ASTType.SymbolicAtom:
            return str(operation.symbol)
        elif operation.ast_type == clingo.ast.ASTType.SymbolicTerm:
            return str(operation.symbol)
        elif operation.ast_type == clingo.ast.ASTType.Variable:
            return variable_assignments[str(operation.name)]
        elif operation.ast_type == clingo.ast.ASTType.UnaryOperation:
            return (
                cls.generate_unary_operator_domain(
                    operation.operator_type,
                    cls.generate_domain(variable_assignments, operation.argument),
                )
            )[0]
        elif operation.ast_type == clingo.ast.ASTType.BinaryOperation:
            res = cls.evaluate_binary_operation(
                operation.operator_type,
                cls.evaluate_operation(operation.left, variable_assignments),
                cls.evaluate_operation(operation.right, variable_assignments),
            )

            return res

        print(
            f"[WARNING] - The compare evaluation operation for {operation}, "
            + f"which is of type {operation.ast_type} is not supported"
        )
        return "NOT-IMPLEMENTED"

    @classmethod
    def apply_unary_operation(cls, domain, unary_operation):
        """
        @domain - Domain-list.
        @unary_operation - Unary AST operation.
        Compute the new domain.
        """
        new_domain = {}

        for element in domain:
            res = unary_operation(int(element))

            if res not in new_domain:
                new_domain[res] = res

        return list(new_domain.keys())

    @classmethod
    def apply_binary_operation(cls, left_domain, right_domain, binary_operation):
        """
        @left_domain - Domain-list.
        @right_domain - Domain-list.
        @binary_operation - Binary AST operation.
        Compute the new domain.
        """
        new_domain = {}

        for left in left_domain:
            for right in right_domain:
                res = binary_operation(int(left), int(right))

                if res not in new_domain:
                    new_domain[res] = res

        return list(new_domain.keys())

    @classmethod
    def aggregate_count_special_variable_getter(cls, binary_operation):
        """
        @binary_operation - AST binary-operation
        Special method for count-aggregate, for increased performance.
        Deprecated.
        """
        if (
            binary_operation.ast_type is clingo.ast.ASTType.BinaryOperation
            and binary_operation.operator_type == int(clingo.ast.BinaryOperator.XOr)
        ):
            return [(str(binary_operation.left), str(binary_operation.right))]

        elif (
            binary_operation.ast_type is clingo.ast.ASTType.BinaryOperation
            and binary_operation.operator_type == int(clingo.ast.BinaryOperator.Or)
        ):
            return cls.aggregate_count_special_variable_getter(
                binary_operation.left
            ) + cls.aggregate_count_special_variable_getter(binary_operation.right)

        assert False  # not implemented
