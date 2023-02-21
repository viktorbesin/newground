import os
import sys
import re

import argparse

import clingo
from clingo.ast import Transformer, Variable, parse_string

from .comparison_tools import ComparisonTools

class TermTransformer(Transformer):
    def __init__(self, printer, no_show=False):
        self.terms = []
        #self.sub_doms = sub_doms
        self.facts = {}
        self.ng_heads = {}
        self.ng = False
        self.show = False
        self.shows = {}
        self.no_show = no_show
        self.printer = printer

        self.current_head = None
        self.current_head_functions = []
        self.safe_variable_rules = {}

        self.domain = {}
        self.comparison_operators_variables = {}

        self.current_comparison = None
        self.current_function = None
        self.current_function_position = 0

        self.current_rule_position = 0

    def visit_Rule(self, node):
        self.current_head = node.head
        self.current_head_functions.append(str(node.head))

        self.visit_children(node)

        pred = str(node.head).split('(', 1)[0]
        arguments = re.sub(r'^.*?\(', '', str(node.head))[:-1].split(',')
        arity = len(arguments)

        if self.ng:
            self.ng = False
            if str(node.head) != "#false":
                # save pred and arity for later use
                if pred not in self.ng_heads:
                    self.ng_heads[pred] = {arity}
                else:
                    self.ng_heads[pred].add(arity)
        elif node.body.__len__() == 0:
            arguments = ','.join(arguments)
            if pred not in self.facts:
                self.facts[pred] = {}
                self.facts[pred][arity] = {arguments}
            elif arity not in self.facts[pred]:
                self.facts[pred][arity] = {arguments}
            else:
                self.facts[pred][arity].add(arguments)


        self.current_rule_position += 1
        self._reset_temporary_rule_variables()
        return node

    def visit_Aggregate(self, node):

        if str(node) == str(self.current_head):
            for elem in node.elements:
                self.current_head_functions.append(str(elem.literal))

        self.visit_children(node)

        return node


    def _reset_temporary_rule_variables(self):
        self.current_head = None
        self.current_head_functions = []

    def _reset_temporary_function_variables(self):
        self.current_function = None
        self.current_function_position = 0

    def _reset_temporary_comparison_variables(self):
        self.current_comparison = None

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

    def _add_safe_variable(self, identifier, position, value, safe_type):


        rule = str(self.current_rule_position)
        if rule not in self.safe_variable_rules:
            self.safe_variable_rules[rule] = {}

        if str(value) not in self.safe_variable_rules[rule]:
            self.safe_variable_rules[rule][str(value)] = []

        to_add_dict = {}
        to_add_dict["type"] = str(safe_type)
        to_add_dict["name"] = str(identifier)
        to_add_dict["position"] = str(position)

        self.safe_variable_rules[rule][str(value)].append(to_add_dict)

    def _add_comparison_to_safe_variables(self, value, operation):

        arguments = ComparisonTools.get_arguments_from_operation(operation)
        variables = []
        for argument in arguments:
            if argument.ast_type == clingo.ast.ASTType.Variable:
                variables.append(str(argument))

        rule = str(self.current_rule_position)
        if rule not in self.safe_variable_rules:
            self.safe_variable_rules[rule] = {}

        if str(value) not in self.safe_variable_rules[rule]:
            self.safe_variable_rules[rule][str(value)] = []

        to_add_dict = {}
        to_add_dict["type"] = "term"
        to_add_dict["variables"] = variables
        to_add_dict["operation"] = operation

        self.safe_variable_rules[rule][str(value)].append(to_add_dict)


    def visit_Function(self, node):

        self.current_function = node

        # shows
        #if not str(node.name).startswith('_dom_'):
        if node.name in self.shows:
            self.shows[node.name].add(len(node.arguments))
        else:
            self.shows[node.name] = {len(node.arguments)}

        self.visit_children(node)

        self._reset_temporary_function_variables()

        return node

    def visit_Comparison(self, node):

        self.current_comparison = node

        if node.comparison == int(clingo.ast.ComparisonOperator.Equal):
            if node.left.ast_type == clingo.ast.ASTType.Variable:
                self._add_comparison_to_safe_variables(str(node.left), node.right)

            if node.right.ast_type == clingo.ast.ASTType.Variable: 
                self._add_comparison_to_safe_variables(str(node.right), node.left)
   
        self.visit_children(node)

        self._reset_temporary_comparison_variables()

        return node

    def _add_comparison(self, rule_name, variable, comparison):
        
        if rule_name not in self.comparison_operators_variables:
            self.comparison_operators_variables[rule_name] = {}

        if variable not in self.comparison_operators_variables[rule_name]:
            self.comparison_operators_variables[rule_name][variable] = []

        self.comparison_operators_variables[rule_name][variable].append(comparison)

    def visit_Variable(self, node):

        if self.current_function and str(self.current_function) not in self.current_head_functions:
            self._add_safe_variable(self.current_function.name, self.current_function_position, str(node), "function")
            self.current_function_position += 1

        if self.current_comparison:

            self._add_comparison(str(self.current_rule_position), str(node), self.current_comparison)

        self.ng = True
        return node

    def visit_Interval(self, node):

        if self.current_function: 
            for value in range(int(str(node.left)), int(str(node.right)) + 1):
                self._add_symbolic_term_to_domain(self.current_function.name, self.current_function_position, str(value))

            self.current_function_position += 1

        for i in range(int(str(node.left)), int(str(node.right))+1):
            if (str(i) not in self.terms):
                self.terms.append(str(i))

        return node

    def visit_SymbolicTerm(self, node):
       
        if self.current_function: 
            self._add_symbolic_term_to_domain(self.current_function.name, self.current_function_position, str(node))
            self.current_function_position += 1

        if (str(node) not in self.terms):
            self.terms.append(str(node))

        return node

    def visit_ShowSignature(self, node):
        self.show = True
        if not self.no_show:
            self.printer.custom_print(node)
        return node


