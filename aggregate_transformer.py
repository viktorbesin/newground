import os
import sys

import argparse

import clingo

from clingo.ast import Transformer, Variable, parse_string

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

    def start(self, contents):

        vrt = AggregateTransformer()
        #parse_string(contents, lambda stm: print(str(vrt(stm))))
        parse_string(contents, lambda stm: do_nothing(vrt(stm)))


        print('\n'.join(vrt.new_prg))



class AggregateTransformer(Transformer):
    
    def __init__(self):
        self.new_prg = []
        self.aggregate_count = 0

        self.cur_has_aggregate = False
        self.cur_aggregates = []

    def reset_temporary_variables(self):

        self.cur_has_aggregate = False
        self.cur_aggregates = []


    def _add_aggregate_helper_rules(self, aggregate_index):
        aggregate = self.cur_aggregates[aggregate_index]

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        if str_type == "sum":
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

        else: 
            assert(False) # Not Implemented

    def _new_aggregate_rule(self, aggregate_index):

        aggregate = self.cur_aggregates[aggregate_index]

        remaining_body = []

        str_type = aggregate["function"][1]
        str_id = aggregate["id"] 

        remaining_body.append(f"{str_type}_ag{str_id}(S{aggregate_index})")

        if aggregate["left_guard"]:
            guard = aggregate["left_guard"]
            remaining_body.append(f"{guard.term} {getCompOperator(guard.comparison)} S{aggregate_index}")
        if aggregate["right_guard"]:
            guard = aggregate["right_guard"]
            remaining_body.append(f"S{aggregate_index} {getCompOperator(guard.comparison)} {guard.term}")

        return remaining_body

    def visit_Rule(self, node):

        self.visit_children(node)

        if not self.cur_has_aggregate:
            self.new_prg.append(str(node))

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
