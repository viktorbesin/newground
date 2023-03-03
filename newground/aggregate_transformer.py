import os
import sys

from enum import Enum

import argparse

import clingo

from clingo.ast import Transformer, Variable, parse_string

from .comparison_tools import ComparisonTools

class AggregateMode(Enum):
    REWRITING = 1
    REPLACE = 2
    REWRITING_NO_BODY = 3

def do_nothing(stuff):
    pass

class AggregateTransformer(Transformer):
    
    def __init__(self, aggregate_mode):
        self.aggregate_mode = aggregate_mode

        self.new_prg = []
        self.aggregate_count = 0

        self.shown_predicates = []

        self.cur_has_aggregate = False
        self.cur_aggregates = []

    def reset_temporary_variables(self):

        self.cur_has_aggregate = False
        self.cur_aggregates = []

    def visit_Program(self, node):

        if node.name == 'rules':
            self.rules = True
            self.new_prg.append(str(node))
        else:
            self.rules = False

        return node


    def visit_Function(self, node):

        self.shown_predicates.append(f"#show {node.name}/{len(node.arguments)}.")

        return node

    def _add_aggregate_helper_rules(self, aggregate_index):
        aggregate = self.cur_aggregates[aggregate_index]
        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 


        remaining_body = []
        if self.aggregate_mode == AggregateMode.REWRITING:


            if str_type == "sum":

                remaining_body.append(f"{str_type}_ag{str_id}(S{aggregate_index})")

                if aggregate["left_guard"]:
                    guard = aggregate["left_guard"]
                    remaining_body.append(f"{guard.term} {ComparisonTools.getCompOperator(guard.comparison)} S{aggregate_index}")
                if aggregate["right_guard"]:
                    guard = aggregate["right_guard"]
                    remaining_body.append(f"S{aggregate_index} {ComparisonTools.getCompOperator(guard.comparison)} {guard.term}")

                self._add_sum_aggregate_rules(aggregate_index)
            elif str_type == "count":

                if aggregate["left_guard"]:
                    guard = aggregate["left_guard"]
                    left_name = f"{str_type}_ag{str_id}_left(1)"
                    remaining_body.append(left_name)
                if aggregate["right_guard"]:
                    guard = aggregate["right_guard"]
                    right_name = f"not {str_type}_ag{str_id}_right(1)"
                    remaining_body.append(right_name)

                self._add_count_aggregate_rules(aggregate_index)
            elif str_type == "min":
                remaining_body += self._add_min_aggregate_rules(aggregate_index)
            elif str_type == "max":
                remaining_body += self._add_max_aggregate_rules(aggregate_index)
            else: 
                assert(False) # Not Implemented
        elif self.aggregate_mode == AggregateMode.REWRITING_NO_BODY and (str_type == "count" or str_type == "max" or str_type == "min"):

            if str_type == "count":
                if aggregate["left_guard"]:
                    guard = aggregate["left_guard"]
                    left_name = f"{str_type}_ag{str_id}_left(1)"
                    remaining_body.append(left_name)
                if aggregate["right_guard"]:
                    guard = aggregate["right_guard"]
                    right_name = f"not {str_type}_ag{str_id}_right(1)"
                    remaining_body.append(right_name)

                self._add_count_aggregate_rules(aggregate_index)
            elif str_type == "min":
                remaining_body += self._add_min_aggregate_rules(aggregate_index)
            elif str_type == "max":
                remaining_body += self._add_max_aggregate_rules(aggregate_index)


        elif self.aggregate_mode == AggregateMode.REPLACE:

            aggregate_helper_name = f"{str_type}_ag{str_id}"
            remaining_body.append(aggregate_helper_name)

            aggregate = self.cur_aggregates[aggregate_index]
            elements = aggregate["elements"]

            str_type = aggregate["function"][1]
            str_id = aggregate["id"] 

            element_predicate_names = []

            for element_index in range(len(elements)):
                element = aggregate["elements"][element_index]
                element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"
                element_body = f"{element_predicate_name}({','.join(element['terms'])})"
                
                body_string = f"{element_body} :- {','.join(element['condition'])}."
                self.new_prg.append(body_string)
                element_predicate_names.append(element_predicate_name)

            self.new_prg.append(f"#program {str_type}.")


            new_elements = []

            for element_index in range(len(elements)):
                element = aggregate["elements"][element_index]

                element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"
                element_body = f"{element_predicate_name}({','.join(element['terms'])})"
 

                new_element = f"{','.join(element['terms'])} : {element_body}"

                new_elements.append(new_element)

            new_rule = f"{aggregate_helper_name} :- "

            if aggregate["left_guard"]:
                left_guard = aggregate["left_guard"]
                left_guard_term = str(left_guard.term)

                operator = ComparisonTools.getCompOperator(left_guard.comparison)

                new_rule += f"{left_guard_term} {operator} "

            new_rule += f"#{str_type}{{{';'.join(new_elements)}}}"

            if aggregate["right_guard"]:
                right_guard = aggregate["right_guard"]
                right_guard_term = str(right_guard.term)

                operator = ComparisonTools.getCompOperator(right_guard.comparison)

                new_rule += f" {operator} {right_guard_term}"

            new_rule += "."

            self.new_prg.append(new_rule)

        else:
            print(f"Aggregate mode {self.aggregate_mode} not implemented!")
            assert(False)

        return remaining_body

    def _add_min_aggregate_rules(self, aggregate_index):
        aggregate = self.cur_aggregates[aggregate_index]
        elements = aggregate["elements"]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        remaining_body = []

        element_predicate_names = []

        if self.aggregate_mode == AggregateMode.REWRITING:
            for element_index in range(len(elements)):
                element = aggregate["elements"][element_index]
                element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"
                element_body = f"{element_predicate_name}({','.join(element['terms'])})"
                
                body_string = f"{element_body} :- {','.join(element['condition'])}."
                self.new_prg.append(body_string)
                element_predicate_names.append(element_predicate_name)

        self.new_prg.append(f"#program {str_type}.")

        if aggregate["left_guard"]:
            left_guard = aggregate["left_guard"]

            left_name = f"{str_type}_ag{str_id}_left(1)"

            left_guard_term = str(left_guard.term)
            count = int(left_guard_term) # Assuming constant

            operator = ComparisonTools.getCompOperator(left_guard.comparison)
            if operator == "<":
                new_operator = "<="
                remaining_body.append(f"not {left_name}")
            elif operator == "<=":
                new_operator = "<"
                remaining_body.append(f"not {left_name}")
            elif operator == ">=":
                new_operator = "<="
                remaining_body.append({left_name})
            elif operator == ">":
                new_operator = "<"
                remaining_body.append({left_name})
            else:
                assert(False) # Not implemented

            for element_index in range(len(elements)):
                element = elements[element_index]
                bodies = self._add_min_max_aggregate_helper(element, element_index, new_operator, left_guard_term)
                rule_string = f"{left_name} :- {','.join(bodies)}."
                self.new_prg.append(rule_string)
 
        if aggregate["right_guard"]:
            right_guard = aggregate["right_guard"]

            right_name = f"{str_type}_ag{str_id}_right(1)"

            right_guard_term = str(right_guard.term)
            count = int(right_guard_term) # Assuming constant

            operator = ComparisonTools.getCompOperator(right_guard.comparison)
            if operator == "<":
                new_operator = "<"
                remaining_body.append(right_name)
            elif operator == "<=":
                new_operator = "<="
                remaining_body.append(right_name)
            else:
                assert(False) # Not implemented

            for element_index in range(len(elements)):
                element = elements[element_index]
                bodies = self._add_min_max_aggregate_helper(element, element_index, new_operator, right_guard_term)
                rule_string = f"{right_name} :- {','.join(bodies)}."
                self.new_prg.append(rule_string)

        return remaining_body

    def _add_min_max_aggregate_helper(self, element, element_index, new_operator, guard_term):

        bodies = []

        terms = []
        for term in element["terms"]:
            terms.append(f"{term}_{str(element_index)}")

        if self.aggregate_mode == AggregateMode.REWRITING:
            body = f"{element_predicate_names[element_index]}({','.join(terms)}), {terms[0]} {new_operator} {guard_term}"
            bodies.append(body)

        elif self.aggregate_mode == AggregateMode.REWRITING_NO_BODY:

            new_conditions = []
            for condition in element["condition"]:
                if "arguments" in condition: # is a function

                    new_arguments = []
                    for argument in condition["arguments"]:
                        if "variable" in argument:
                            new_arguments.append(f"{argument['variable']}_{element_index}")
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

                    for argument in ComparisonTools.get_arguments_from_operation(comparison.left):
                        if argument.ast_type == clingo.ast.ASTType.Variable:
                            variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}"

                    for argument in ComparisonTools.get_arguments_from_operation(comparison.right):
                        if argument.ast_type == clingo.ast.ASTType.Variable:
                            variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}"


                    instantiated_left = ComparisonTools.instantiate_operation(comparison.left, variable_assignments)
                    instantiated_right = ComparisonTools.instantiate_operation(comparison.right, variable_assignments)

                    new_conditions.append(ComparisonTools.comparison_handlings(comparison.comparison, instantiated_left, instantiated_right))

                else:
                    assert(False) # Not implemented

            new_conditions.append(f"{terms[0]} {new_operator} {guard_term}")

            bodies += new_conditions

        return bodies
            

    def _add_max_aggregate_rules(self, aggregate_index):
        aggregate = self.cur_aggregates[aggregate_index]
        elements = aggregate["elements"]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        remaining_body = []

        element_predicate_names = []

        if self.aggregate_mode == AggregateMode.REWRITING:
            for element_index in range(len(elements)):
                element = aggregate["elements"][element_index]
                element_predicate_name = f"body_{str_type}_ag{str_id}_{element_index}"
                element_body = f"{element_predicate_name}({','.join(element['terms'])})"
                
                body_string = f"{element_body} :- {','.join(element['condition'])}."
                self.new_prg.append(body_string)
                element_predicate_names.append(element_predicate_name)

        self.new_prg.append(f"#program {str_type}.")

        if aggregate["left_guard"]:
            left_guard = aggregate["left_guard"]

            left_name = f"{str_type}_ag{str_id}_left(1)"

            left_guard_term = str(left_guard.term)
            count = int(left_guard_term) # Assuming constant

            operator = ComparisonTools.getCompOperator(left_guard.comparison)
            if operator == "<":
                new_operator = ">"
                remaining_body.append(f"{left_name}")
            elif operator == "<=":
                new_operator = ">="
                remaining_body.append(f"{left_name}")
            else:
                assert(False) # Not implemented

            for element_index in range(len(elements)):
                element = elements[element_index]
                bodies = self._add_min_max_aggregate_helper(element, element_index, new_operator, left_guard_term)
                rule_string = f"{left_name} :- {','.join(bodies)}."
                self.new_prg.append(rule_string)
            
        if aggregate["right_guard"]:
            right_guard = aggregate["right_guard"]

            right_name = f"{str_type}_ag{str_id}_right(1)"

            right_guard_term = str(right_guard.term)
            count = int(right_guard_term) # Assuming constant

            operator = ComparisonTools.getCompOperator(right_guard.comparison)
            if operator == "<":
                new_operator = ">="
                remaining_body.append(f"not {right_name}")
            elif operator == "<=":
                new_operator = ">"
                remaining_body.append(f"not {right_name}")
            else:
                assert(False) # Not implemented

            for element_index in range(len(elements)):
                element = elements[element_index]
                bodies = self._add_min_max_aggregate_helper(element, element_index, new_operator, right_guard_term)
                rule_string = f"{right_name} :- {','.join(bodies)}."
                self.new_prg.append(rule_string)

        return remaining_body
            

    def _add_count_aggregate_rules(self, aggregate_index):

        aggregate = self.cur_aggregates[aggregate_index]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 


        if self.aggregate_mode == AggregateMode.REWRITING:
            for element_index in range(len(aggregate["elements"])):
                element = aggregate["elements"][element_index]
                body_string = f"body_{str_type}_ag{str_id}_{element_index}({','.join(element['terms'])}) :- {','.join(element['condition'])}."
                self.new_prg.append(body_string)

        self.new_prg.append(f"#program {str_type}.")

        new_atoms = []
        if aggregate["left_guard"]:
            left_guard = aggregate["left_guard"]

            left_name = f"{str_type}_ag{str_id}_left(1)"

            count = int(str(left_guard.term)) # Assuming constant

            operator = ComparisonTools.getCompOperator(left_guard.comparison)
            if operator == "<":
                count += 1
            elif operator == "<=":
                count = count
            else:
                assert(False) # Not implemented

            bodies, helper_bodies = self._count_generate_bodies_and_helper_bodies(count, aggregate["elements"], str_type, str_id)

            rule_string = f"{left_name} :- {','.join(bodies + helper_bodies)}."

            self.new_prg.append(rule_string)
        
        if aggregate["right_guard"]:
            right_guard = aggregate["right_guard"]

            right_name = f"{str_type}_ag{str_id}_right(1)"

            count = int(str(right_guard.term)) # Assuming constant

            operator = ComparisonTools.getCompOperator(left_guard.comparison)
            if operator == "<":
                count = count
            elif operator == "<=":
                count += 1
            else:
                assert(False) # Not implemented

            bodies, helper_bodies = self._count_generate_bodies_and_helper_bodies(count,  aggregate["elements"], str_type, str_id)

            rule_string = f"{right_name} :- {','.join(bodies + helper_bodies)}."

            self.new_prg.append(rule_string)



    def _count_generate_bodies_and_helper_bodies(self, count, elements, str_type, str_id):

        terms = []
        bodies = []
        for element_index in range(len(elements)):
            element = elements[element_index]

            for index in range(count):
                new_terms = []
                for term in element["terms"]:
                    new_terms.append(f"{str(term)}_{str(element_index)}_{str(index)}")

                terms.append(new_terms)

                if self.aggregate_mode == AggregateMode.REWRITING:
                    bodies.append(f"body_{str_type}_ag{str_id}_{element_index}({','.join(new_terms)})") 
                elif self.aggregate_mode == AggregateMode.REWRITING_NO_BODY:


                    new_conditions = []

                    for condition in element["condition"]:

                        if "arguments" in condition:

                            new_condition = condition["name"]

                            new_args = []


                            for argument in condition["arguments"]:
                                if "variable" in argument:
                                    variable = argument["variable"]

                                    new_args.append(f"{variable}_{str(element_index)}_{str(index)}")
                                elif "term" in argument:
                                    new_args.append(f"{argument['term']}")

                            if len(new_args) > 0:
                                new_condition += f"({','.join(new_args)})"

                            new_conditions.append(new_condition)
                        elif "comparison" in condition:
                            comparison = condition["comparison"]

                            variable_assignments = {}

                            for argument in ComparisonTools.get_arguments_from_operation(comparison.left):
                                if argument.ast_type == clingo.ast.ASTType.Variable:
                                    variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}_{str(index)}"

                            for argument in ComparisonTools.get_arguments_from_operation(comparison.right):
                                if argument.ast_type == clingo.ast.ASTType.Variable:
                                    variable_assignments[str(argument)] = f"{str(argument)}_{str(element_index)}_{str(index)}"


                            instantiated_left = ComparisonTools.instantiate_operation(comparison.left, variable_assignments)
                            instantiated_right = ComparisonTools.instantiate_operation(comparison.right, variable_assignments)

                            new_conditions.append(ComparisonTools.comparison_handlings(comparison.comparison, instantiated_left, instantiated_right))


                        else:
                            assert(False) # Not implemented

                    bodies.append(f"{','.join(new_conditions)}")

        helper_bodies = []
        for index_1 in range(len(terms)):
            for index_2 in range(index_1 + 1, len(terms)):

                helper_body = "0 != "

                term_length = min(len(terms[index_1]), len(terms[index_2])) 

                term_combinations = [] 
                for term_index in range(term_length):
                    first_term = terms[index_1][term_index]
                    second_term = terms[index_2][term_index]

                    term_combinations.append(f"({first_term} ^ {second_term})")

                helper_body = f"0 != {'?'.join(term_combinations)}"
                helper_bodies.append(helper_body)

        return (bodies, helper_bodies)



    def _add_sum_aggregate_rules(self, aggregate_index):
        """
            Adds the necessary rules for the recursive sum aggregate.
        """

        aggregate = self.cur_aggregates[aggregate_index]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        
        self.new_prg.append(f"#program {str_type}.")

        rule_string = f"{str_type}_ag{str_id}(S) :- "
       
        element_strings = []
        element_variables = [] 

        for element_id in range(len(aggregate["elements"])):
            element = aggregate["elements"][element_id]

            element_strings.append(f"{str_type}_ag{str_id}_elem{element_id}(S{element_id})")
            element_variables.append(f"S{element_id}")

        rule_string += ','.join(element_strings)

        rule_string += f", S = {'+'.join(element_variables)}."

        self.new_prg.append(rule_string)

        for element_id in range(len(aggregate["elements"])):

            element = aggregate["elements"][element_id]
            guard = aggregate["right_guard"]
            # Body
            body_head_def = f"body_ag{str_id}_elem{element_id}({','.join(element['terms'])})"
            body_head_def_first = element['terms'][0]
            body_head_def_terms = ','.join(element['terms'])

            # DRY VIOLATION START: DRY (Do Not Repeat) justification: Because it is only used here and writing a subroutine creates more overload than simply duplicating the code
            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "1")
            body_head_1 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_1_first = term_strings_temp[0]
            body_head_1_def_terms = ','.join(term_strings_temp)
             
            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "2")
            body_head_2 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_2_first = term_strings_temp[0]
            body_head_2_def_terms = ','.join(term_strings_temp)

            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "3")
            body_head_3 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_3_first = term_strings_temp[0]
            body_head_3_def_terms = ','.join(term_strings_temp)
            # DRY VIOLATION END

            if len(element['condition']) > 0:
                rule_string = f"{body_head_def} :- {','.join(element['condition'])}."
            else:
                rule_string = f"{body_head_def}."

            self.new_prg.append(rule_string)

            # Partial Sum Last

            rule_string = f"{str_type}_ag{str_id}_elem{element_id}(S) :- last_ag{str_id}_elem{element_id}({body_head_def_terms}), partial_{str_type}_ag{str_id}_elem{element_id}({body_head_def_terms},S)."
            self.new_prg.append(rule_string)

            # Partial Sum Middle

            rule_string = f"partial_{str_type}_ag{str_id}_elem{element_id}({body_head_2_def_terms},S2) :- next_ag{str_id}_elem{element_id}({body_head_1_def_terms},{body_head_2_def_terms}), partial_{str_type}_ag{str_id}_elem{element_id}({body_head_1_def_terms},S1), S2 = S1 + {body_head_2_first}, S2 <= {guard.term}."
            self.new_prg.append(rule_string)

            # Partial Sum First

            rule_string = f"partial_{str_type}_ag{str_id}_elem{element_id}({body_head_def_terms},S) :- first_ag{str_id}_elem{element_id}({body_head_def_terms}), S = {body_head_def_terms}."
            self.new_prg.append(rule_string)

            # not_last
            rule_string = f"not_last_ag{str_id}_elem{element_id}({body_head_1_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}."
            self.new_prg.append(rule_string)

            # Last
            rule_string = f"last_ag{str_id}_elem{element_id}({body_head_def_terms}) :- {body_head_def}, not not_last_ag{str_id}_elem{element_id}({body_head_def_terms})."
            self.new_prg.append(rule_string)

            # not_next
            rule_string = f"not_next_ag{str_id}_elem{element_id}({body_head_1_def_terms}, {body_head_2_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_3}, {body_head_1} < {body_head_3}, {body_head_3} < {body_head_2}."
            self.new_prg.append(rule_string)

            # next
            rule_string = f"next_ag{str_id}_elem{element_id}({body_head_1_def_terms}, {body_head_2_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}, not not_next_ag{str_id}_elem{element_id}({body_head_1_def_terms}, {body_head_2_def_terms})."
            self.new_prg.append(rule_string)

            # not_first
            rule_string = f"not_first_ag{str_id}_elem{element_id}({body_head_2_def_terms}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}."
            self.new_prg.append(rule_string)

            # first
            rule_string = f"first_ag{str_id}_elem{element_id}({body_head_1_def_terms}) :- {body_head_1}, not not_first_ag{str_id}_elem{element_id}({body_head_1_def_terms})."
            self.new_prg.append(rule_string)


    def visit_Rule(self, node):

        self.visit_children(node)

        if not self.cur_has_aggregate or not self.rules:
            body_rep = ""
            for body_element_index in range(len(node.body)):
                body_elem = node.body[body_element_index]
                if body_element_index < len(node.body) - 1:
                    body_rep += f"{str(body_elem)},"
                else:
                    body_rep += f"{str(body_elem)}"

            if len(node.body) > 0:
                self.new_prg.append(f"{str(node.head)} :- {body_rep}.")
            else:    
                self.new_prg.append(f"{str(node.head)}.")

        else:
            head = str(node.head)
            remaining_body = []

            for body_item in node.body:
                if body_item.atom.ast_type != clingo.ast.ASTType.BodyAggregate:
                    remaining_body.append(str(body_item))

            for aggregate_index in range(len(self.cur_aggregates)):
                aggregate = self.cur_aggregates[aggregate_index]
                str_type = aggregate["function"][1]
                remaining_body += self._add_aggregate_helper_rules(aggregate_index)
                self.new_prg.append(f"#program rules.")

            remaining_body_string = ','.join(remaining_body)
            new_rule = f"{head} :- {remaining_body_string}."
            self.new_prg.append(new_rule)

        self.reset_temporary_variables() # MUST BE LAST
        return node

    def visit_BodyAggregate(self, node):

        self.cur_has_aggregate = True

        aggregate_dict = {}
        aggregate_dict["left_guard"] = node.left_guard
        aggregate_dict["right_guard"] = node.right_guard

        if node.function == 0:
            function = (0,"count")
        elif node.function == 1:
            function = (1,"sum")
        elif node.function == 2:
            function = (2, "sumplus")
        elif node.function == 3:
            function = (3, "min")
        elif node.function == 4:
            function = (4, "max")
        else:
            print(node.function)
            assert(False) # Not Implemented

        aggregate_dict["function"] = function

        aggregate_dict["id"] = self.aggregate_count
        self.aggregate_count += 1

        aggregate_dict["elements"] = []

        for element in node.elements:
            self.visit_BodyAggregateElement(element, aggregate_dict = aggregate_dict)
        
        self.cur_aggregates.append(aggregate_dict)

        return node
        

    def visit_BodyAggregateElement(self, node, aggregate_dict = None):

        if aggregate_dict:

            element_dict = {}

            term_strings = []
            for term in node.terms:
                term_strings.append(str(term))

            element_dict["terms"] = term_strings

            condition_strings = []
            for condition in node.condition:

                if self.aggregate_mode == AggregateMode.REWRITING_NO_BODY:
                    if hasattr(condition, "atom") and hasattr(condition.atom, "symbol") and condition.atom.symbol.ast_type == clingo.ast.ASTType.Function:
                        cur_dict = {}
                        cur_dict["all"] = str(condition)
                        cur_dict["name"] = str(condition.atom.symbol.name) 
                        cur_dict["arguments"] = []


                        for argument in condition.atom.symbol.arguments:
                            if argument.ast_type == clingo.ast.ASTType.Variable:
                                variable_argument = {}
                                variable_argument["variable"] = str(argument)
                                
                                cur_dict["arguments"].append(variable_argument)

                            elif argument.ast_type == clingo.ast.ASTType.SymbolicTerm:
                                term_argument = {}
                                term_argument["term"] = str(argument)
                                
                                cur_dict["arguments"].append(term_argument)

                            else:
                                print(argument)
                                print(argument.ast_type)
                                print("NOT IMPLEMENTED")
                                assert(False) # Not implemented

                        condition_strings.append(cur_dict)
                    elif hasattr(condition, "atom") and condition.atom.ast_type == clingo.ast.ASTType.Comparison:
                        cur_dict = {}
                        cur_dict["all"] = str(condition)
                        cur_dict["comparison"] = condition.atom

                        condition_strings.append(cur_dict)

                    else:
                        print(condition)
                        print(condition.ast_type)
                        assert(False)
                    

                else:
                    condition_strings.append(str(condition))

            element_dict["condition"] = condition_strings

            aggregate_dict["elements"].append(element_dict) 

        return node

    def visit_Variable(self, node):
        return node

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='newground', usage='%(prog)s [files]')
    parser.add_argument('--no-show', action='store_true', help='Do not print #show-statements to avoid compatibility issues. ')
    parser.add_argument('--ground-guess', action='store_true',
                        help='Additionally ground guesses which results in (fully) grounded output. ')
    parser.add_argument('--ground', action='store_true',
                        help='Output program fully grounded. ')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    # no output from clingo itself
    sys.argv.append("--outf=3")
    no_show = False
    ground_guess = False
    ground = False
 
    total_contents = ""
 
    for f in args.files:
        file_contents = open(f, 'r').read()
        total_contents += file_contents

    if args.no_show:
        sys.argv.remove('--no-show')
        no_show = True
    if args.ground_guess:
        sys.argv.remove('--ground-guess')
        ground_guess = True
    if args.ground:
        sys.argv.remove('--ground')
        ground_guess = True
        ground = True

    handler = AggregateHandler()
    handler.start(total_contents)
