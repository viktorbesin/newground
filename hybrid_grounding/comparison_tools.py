import clingo

class ComparisonTools:

    @classmethod
    def getCompOperator(cls, comp):
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
        else:
            assert(False) # not implemented

    @classmethod
    def comparison_handlings(cls, comp, c1, c2):
        if comp is int(clingo.ast.ComparisonOperator.Equal): # == 5
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
        else:
            assert(False) # not implemented


    @classmethod
    def compareTerms(cls, comp, c1, c2):
        if comp is int(clingo.ast.ComparisonOperator.Equal): # == 5
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
        else:
            assert(False) # not implemented

    @classmethod
    def get_arguments_from_operation(cls, root):
        """
            Performs a tree traversal of an operation (e.g. X+Y -> first ''+'', then ''X'' and lastly ''Y'' -> then combines together)
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            return cls.get_arguments_from_operation(root.left) + cls.get_arguments_from_operation(root.right)

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            return cls.get_arguments_from_operation(root.argument)

        elif root.ast_type is clingo.ast.ASTType.Variable or root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return [root]
        elif root.ast_type is clingo.ast.ASTType.Function:

            argument_list = []

            for argument in root.arguments:
                argument_list += cls.get_arguments_from_operation(argument)

            return argument_list

        else:
            assert(False) # not implemented

    @classmethod
    def instantiate_operation(cls, root, variable_assignments):
        """
            Instantiates a operation and returns a string
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            string_rep = cls._get_binary_operator_type_as_string(root.operator_type)
    
            return "(" + cls.instantiate_operation(root.left, variable_assignments) + string_rep + cls.instantiate_operation(root.right, variable_assignments) + ")"

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            string_rep = cls._get_unary_operator_type_as_string(root.operator_type)

            if string_rep != "ABSOLUTE":
                return "(" + string_rep + cls.instantiate_operation(root.argument, variable_assignments) + ")"
            elif string_rep == "ABSOLUTE":
                return "(|" + cls.instantiate_operation(root.argument, variable_assignments) + "|)"

        elif root.ast_type is clingo.ast.ASTType.Variable:
            variable_string = str(root)
            return variable_assignments[variable_string]

        elif root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return str(root)

        elif root.ast_type is clingo.ast.ASTType.Function:

            instantiations = []
            for argument in root.arguments:
                instantiations.append(cls.instantiate_operation(argument, variable_assignments))

            return f"{root.name}({','.join(instantiations)})"

        else:
            assert(False) # not implemented

    @classmethod
    def _get_unary_operator_type_as_string(cls, operator_type):
        if operator_type == int(clingo.ast.UnaryOperator.Minus):
            return "-"
        elif operator_type == int(clingo.ast.UnaryOperator.Negation):
            return "~"
        elif operator_type == int(clingo.ast.UnaryOperator.Absolute): # Absolute, i.e. |X| needs special handling
            return "ABSOLUTE"
        else:
            print(f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

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
        else:
            print(f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

       
    @classmethod                     
    def generate_domain(cls, variable_assignments, operation):

        if operation.ast_type == clingo.ast.ASTType.SymbolicAtom: 
            return [str(operation.symbol)]
        elif operation.ast_type == clingo.ast.ASTType.SymbolicTerm:
            return [str(operation.symbol)]
        elif operation.ast_type == clingo.ast.ASTType.Variable:
            return variable_assignments[str(operation.name)]
        elif operation.ast_type == clingo.ast.ASTType.UnaryOperation:
            return cls.generate_unary_operator_domain(operation.operator_type, cls.generate_domain(variable_assignments, operation.argument))
        elif operation.ast_type == clingo.ast.ASTType.BinaryOperation:
            return cls.generate_binary_operator_domain(operation.operator_type, cls.generate_domain(variable_assignments, operation.left), cls.generate_domain(variable_assignments, operation.right))
        else:
            print(operation)
            print(operation.ast_type)
            assert(False)

    @classmethod 
    def generate_unary_operator_domain(cls, operator_type, domain):

        if operator_type == int(clingo.ast.UnaryOperator.Minus):
            return cls.apply_unary_operation(domain, lambda d: -d)
        elif operator_type == int(clingo.ast.UnaryOperator.Negation):
            return cls.apply_unary_operation(domain, lambda d: ~d)
        elif operator_type == int(clingo.ast.UnaryOperator.Absolute): 
            return cls.apply_unary_operation(domain, lambda d: abs(d))
        else:
            print(f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented


    @classmethod
    def generate_binary_operator_domain(cls, operator_type, left_domain, right_domain):

        if operator_type == int(clingo.ast.BinaryOperator.XOr):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l ^ r)
        elif operator_type == int(clingo.ast.BinaryOperator.Or):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l | r)
        elif operator_type == int(clingo.ast.BinaryOperator.And):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l & r)
        elif operator_type == int(clingo.ast.BinaryOperator.Plus):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l + r)
        elif operator_type == int(clingo.ast.BinaryOperator.Minus):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l - r)
        elif operator_type == int(clingo.ast.BinaryOperator.Multiplication):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l * r)
        elif operator_type == int(clingo.ast.BinaryOperator.Division):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l / r)
        elif operator_type == int(clingo.ast.BinaryOperator.Modulo):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: l % r)
        elif operator_type == int(clingo.ast.BinaryOperator.Power):
            return cls.apply_binary_operation(left_domain, right_domain, lambda l,r: pow(l,r))
        else:
            print(f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

        assert(False) # not implemented


    @classmethod
    def evaluate_binary_operation(cls, operator_type, left_value, right_value):

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
        else:
            print(f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

        assert(False) # not implemented

    @classmethod
    def evaluate_operation(cls, operation, variable_assignments):

        if operation.ast_type == clingo.ast.ASTType.SymbolicAtom: 
            return str(operation.symbol)
        elif operation.ast_type == clingo.ast.ASTType.SymbolicTerm:
            return str(operation.symbol)
        elif operation.ast_type == clingo.ast.ASTType.Variable:
            return variable_assignments[str(operation.name)]
        elif operation.ast_type == clingo.ast.ASTType.UnaryOperation:
            return (cls.generate_unary_operator_domain(operation.operator_type, cls.generate_domain(variable_assignments, operation.argument)))[0]
        elif operation.ast_type == clingo.ast.ASTType.BinaryOperation:
            res = cls.evaluate_binary_operation(operation.operator_type, cls.evaluate_operation(operation.left, variable_assignments), cls.evaluate_operation(operation.right, variable_assignments))
            #res = (cls.generate_binary_operator_domain(operation.operator_type, cls.generate_domain(variable_assignments, operation.left), cls.generate_domain(variable_assignments, operation.right)))

            return res
        else:   
            print(f"[WARNING] - The compare evaluation operation for {operation}, which is of type {operation.ast_type} is not supported")
            return "NOT-IMPLEMENTED"

    @classmethod     
    def apply_unary_operation(cls, domain, unary_operation):

        new_domain = {}

        for element in domain:
            res = unary_operation(int(element))

            if res not in new_domain:
                new_domain[res] = res

        return list(new_domain.keys())

    @classmethod
    def apply_binary_operation(cls, left_domain, right_domain, binary_operation):
    
        new_domain = {}

        for left in left_domain:
            for right in right_domain:
                res = binary_operation(int(left), int(right))

                if res not in new_domain:
                    new_domain[res] = res

        return list(new_domain.keys())

    @classmethod
    def aggregate_count_special_variable_getter(cls, binary_operation):
        if binary_operation.ast_type is clingo.ast.ASTType.BinaryOperation and binary_operation.operator_type == int(clingo.ast.BinaryOperator.XOr):
            return [(str(binary_operation.left), str(binary_operation.right))]

        elif binary_operation.ast_type is clingo.ast.ASTType.BinaryOperation and binary_operation.operator_type == int(clingo.ast.BinaryOperator.Or):
            return cls.aggregate_count_special_variable_getter(binary_operation.left) + cls.aggregate_count_special_variable_getter(binary_operation.right)
        else:
            assert(False) # not implemented

