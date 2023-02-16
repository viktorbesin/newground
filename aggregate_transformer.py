import os
import sys

import argparse

import clingo

from clingo.ast import Transformer, Variable, parse_string
from newground import ClingoApp

def do_nothing(stuff):
    pass

def getCompOperator(comp):
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



class AggregateHandler:

    def __init__(self, name="", no_show=False, ground_guess=False, ground=False, output_printer = None):
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground
        self.output_printer = output_printer
        
        self.rules = False

    def start(self, contents):

        vrt = AggregateTransformer()
        parse_string(contents, lambda stm: do_nothing(vrt(stm)))

        shown_predicates = list(set(vrt.shown_predicates))

        program_string = '\n'.join(shown_predicates + vrt.new_prg)

        #print(program_string)
   
        newground = ClingoApp("newground", self.no_show, self.ground_guess, self.ground, self.output_printer)

        newground.main(clingo.Control(), [program_string])



class AggregateTransformer(Transformer):
    
    def __init__(self):
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

        if str_type == "sum":
            self._add_sum_aggregate_rules(aggregate_index)
        elif str_type == "count":

            if len(aggregate["elements"]) > 1:  
                print("Not implemented")
                assert(False) # Not implemented
            
            element = aggregate["elements"][0]

            body_string = f"body_{str_type}_ag{str_id}({','.join(element['terms'])}) :- {','.join(element['condition'])}."
            self.new_prg.append(body_string)

            new_atoms = []
            if aggregate["left_guard"]:
                left_guard = aggregate["left_guard"]

                left_name = f"{str_type}_ag{str_id}_left(1)"

                count = int(str(left_guard.term)) # Assuming constant

                operator = getCompOperator(left_guard.comparison)
                if operator == "<":
                    count += 1
                elif operator == "<=":
                    count = count
                else:
                    assert(False) # Not implemented

                bodies, helper_bodies = self._count_generate_bodies_and_helper_bodies(count, element, str_type, str_id)

                rule_string = f"{left_name} :- {','.join(bodies + helper_bodies)}."

                self.new_prg.append(rule_string)
            
            if aggregate["right_guard"]:
                right_guard = aggregate["right_guard"]

                right_name = f"{str_type}_ag{str_id}_right(1)"

                count = int(str(right_guard.term)) # Assuming constant

                operator = getCompOperator(left_guard.comparison)
                if operator == "<":
                    count = count
                elif operator == "<=":
                    count += 1
                else:
                    assert(False) # Not implemented

                bodies, helper_bodies = self._count_generate_bodies_and_helper_bodies(count, element, str_type, str_id)

                rule_string = f"{right_name} :- {','.join(bodies + helper_bodies)}."

                self.new_prg.append(rule_string)


        else: 
            assert(False) # Not Implemented

    def _count_generate_bodies_and_helper_bodies(self, count, element, str_type, str_id):

        terms = []
        bodies = []
        for index in range(count):
            new_terms = []
            for term in element["terms"]:
                new_terms.append(term + str(index))

            terms.append(new_terms)

            bodies.append(f"body_{str_type}_ag{str_id}({','.join(new_terms)})") 

        term_length = len(terms[0])
        helper_bodies = []
        for index_1 in range(count):
            for index_2 in range(index_1 + 1, count):

                helper_body = "0 != "

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
            # Partial Sum Last

            rule_string = f"{str_type}_ag{str_id}_elem{element_id}(S) :- last_ag{str_id}_elem{element_id}(O,X2), partial_{str_type}_ag{str_id}_elem{element_id}(O,S)."
            self.new_prg.append(rule_string)

            # Partial Sum Middle

            rule_string = f"partial_{str_type}_ag{str_id}_elem{element_id}(O2,S2) :- next_ag{str_id}_elem{element_id}(O1,O2,X2), partial_{str_type}_ag{str_id}_elem{element_id}(O1,S1), S2 = S1 + X2."
            self.new_prg.append(rule_string)

            # Partial Sum First

            rule_string = f"partial_{str_type}_ag{str_id}_elem{element_id}(O,X1) :- first_ag{str_id}_elem{element_id}(O,X1)."
            self.new_prg.append(rule_string)

            # Body
            body_head_def = f"body_ag{str_id}_elem{element_id}({','.join(element['terms'])})"
            body_head_def_first = element['terms'][0]

            # DRY VIOLATION START: DRY (Do Not Repeat) justification: Because it is only used here and writing a subroutine creates more overload than simply duplicating the code
            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "1")
            body_head_1 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_1_first = term_strings_temp[0]
             
            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "2")
            body_head_2 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_2_first = term_strings_temp[0]

            term_strings_temp = []
            for term_string in element['terms']:
                term_strings_temp.append(term_string + "3")
            body_head_3 = f"body_ag{str_id}_elem{element_id}({','.join(term_strings_temp)})"
            body_head_3_first = term_strings_temp[0]
            # DRY VIOLATION END

            if len(element['condition']) > 0:
                rule_string = f"{body_head_def} :- {','.join(element['condition'])}."
            else:
                rule_string = f"{body_head_def}."

            self.new_prg.append(rule_string)


            # not_last
            rule_string = f"not_last_ag{str_id}_elem{element_id}({body_head_1}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}."
            self.new_prg.append(rule_string)

            # Last
            rule_string = f"last_ag{str_id}_elem{element_id}({body_head_def},{body_head_def_first}) :- {body_head_def}, not not_last_ag{str_id}_elem{element_id}({body_head_def})."
            self.new_prg.append(rule_string)

            # not_next
            rule_string = f"not_next_ag{str_id}_elem{element_id}({body_head_1}, {body_head_2}) :- {body_head_1}, {body_head_2}, {body_head_3}, {body_head_1} < {body_head_3}, {body_head_3} < {body_head_2}."
            self.new_prg.append(rule_string)

            # next
            rule_string = f"next_ag{str_id}_elem{element_id}({body_head_1}, {body_head_2}, {body_head_2_first}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}, not not_next_ag{str_id}_elem{element_id}({body_head_1}, {body_head_2})."
            self.new_prg.append(rule_string)

            # not_first
            rule_string = f"not_first_ag{str_id}_elem{element_id}({body_head_2}) :- {body_head_1}, {body_head_2}, {body_head_1} < {body_head_2}."
            self.new_prg.append(rule_string)

            # first
            rule_string = f"first_ag{str_id}_elem{element_id}({body_head_1}, {body_head_1_first}) :- {body_head_1}, not not_first_ag{str_id}_elem{element_id}({body_head_1})."
            self.new_prg.append(rule_string)



    def _new_aggregate_rule(self, aggregate_index):

        aggregate = self.cur_aggregates[aggregate_index]

        remaining_body = []

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        if str_type == "sum":
            remaining_body.append(f"{str_type}_ag{str_id}(S{aggregate_index})")

            if aggregate["left_guard"]:
                guard = aggregate["left_guard"]
                remaining_body.append(f"{guard.term} {getCompOperator(guard.comparison)} S{aggregate_index}")
            if aggregate["right_guard"]:
                guard = aggregate["right_guard"]
                remaining_body.append(f"S{aggregate_index} {getCompOperator(guard.comparison)} {guard.term}")

        elif str_type == "count":
            if aggregate["left_guard"]:
                guard = aggregate["left_guard"]
                left_name = f"{str_type}_ag{str_id}_left(1)"
                remaining_body.append(left_name)
            if aggregate["right_guard"]:
                guard = aggregate["right_guard"]
                right_name = f"not {str_type}_ag{str_id}_right(1)"
                remaining_body.append(right_name)

        else:
            assert(False) # Not Implemented

        return remaining_body

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
                remaining_body += self._new_aggregate_rule(aggregate_index)

                self._add_aggregate_helper_rules(aggregate_index)
                

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
