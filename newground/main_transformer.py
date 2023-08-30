import os 
import sys
import re

import itertools
import argparse
import clingo

from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder, Rule, ComparisonOperator
from clingo.control import Control

from clingox.program import Program, ProgramObserver, Remapping

from .hybrid_grounding.generate_satisfiability_part import GenerateSatisfiabilityPart
from .hybrid_grounding.generate_foundedness_part import GenerateFoundednessPart
from .hybrid_grounding.helper_part import HelperPart


import networkx as nx

from .comparison_tools import ComparisonTools
from .aggregate_transformer import AggregateMode


class MainTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads, shows, ground_guess, ground, printer, domain, safe_variables_rules, aggregate_mode, rule_strongly_restricted_components):
        self.rules = False
        self.count = False
        self.sum = False
        self.min = False
        self.max = False
        
        self.aggregate_mode = aggregate_mode

        self.rule_is_non_ground = False
        self.bld = bld
        self.terms = terms
        self.facts = facts
        self.ng_heads = ng_heads
        #self.sub_doms = sub_doms
        self.ground_guess = ground_guess
        self.ground = ground
        self.printer = printer

        self.domain = domain
        self.safe_variables_rules = safe_variables_rules

        self.rule_anonymous_variables = 0
        self.rule_variables = []
        self.rule_literals = []
        self.rule_literals_signums = []
        self.rule_comparisons = []
        self.shows = shows
        self.foundness ={}
        self.f = {}
        self.counter = 0
        self.non_ground_rules = {}
        self.g_counter = 'A'

        self.current_rule = None
        self.current_comparison = None

        self.unfounded_rules = {}
        self.current_rule_position = 0

        self.rule_strongly_restricted_components = rule_strongly_restricted_components

    def _reset_after_rule(self):
        self.rule_variables = []
        self.rule_literals = []
        self.rule_literals_signums = []
        self.rule_comparisons = []
        self.rule_anonymous_variables = 0
        self.rule_is_non_ground = False
        #self.head = None


    def visit_Minimize(self, node):
        self.printer.custom_print(f"{str(node)}")

        return node


    def visit_Rule(self, node):

        if not self.rules:
            self._reset_after_rule()
            if not self.ground:
                self._outputNodeFormatConform(node)

            self.current_rule_position += 1

            return node

        if (self.count or self.sum or self.min or self.max) and self.aggregate_mode == AggregateMode.REPLACE:
            if not self.ground:
                self._outputNodeFormatConform(node)

            return node # In this mode do nothing here
        
        self.current_rule = node

        self.visit_children(node)

        # if so: handle grounding
        if self.rule_is_non_ground:
            self.non_ground_rules[self.current_rule_position] = self.current_rule_position
            #self.current_rule_position += 1
            if str(node.head) != "#false":
                head = self.rule_literals[0]
            else:
                head = None

            satisfiability_generator = GenerateSatisfiabilityPart(head, 
                                                                  self.current_rule_position,
                                                                  self.printer, self.domain,
                                                                  self.safe_variables_rules,
                                                                  self.rule_variables,
                                                                  self.rule_comparisons,
                                                                  self.rule_literals,
                                                                  self.rule_literals_signums)
            satisfiability_generator.generate_sat_part()

            # FOUND NEW
            if head is not None:
                foundedness_generator = GenerateFoundednessPart(head, 
                                                                  self.current_rule_position,
                                                                  self.printer, self.domain,
                                                                  self.safe_variables_rules,
                                                                  self.rule_variables,
                                                                  self.rule_comparisons,
                                                                  self.rule_literals,
                                                                  self.rule_literals_signums,
                                                                  self.current_rule,
                                                                  self.rule_strongly_restricted_components,
                                                                  self.ground_guess,
                                                                  self.unfounded_rules)
                foundedness_generator.generate_foundedness_part()

        else: # found-check for ground-rules (if needed) (pred, arity, combinations, rule, indices)
            pred = str(node.head).split('(', 1)[0]
            arguments = re.sub(r'^.*?\(', '', str(node.head))[:-1].split(',')
            arity = len(arguments)
            arguments = ','.join(arguments)

            if pred in self.ng_heads and arity in self.ng_heads[pred] \
                    and not (pred in self.facts and arity in self.facts[pred] and arguments in self.facts[pred][arity]):

                for body_atom in node.body:
                    if str(body_atom).startswith("not "):
                        neg = ""
                    else:
                        neg = "not "
                    self.printer.custom_print(f"r{self.g_counter}_unfound({arguments}) :- "
                          f"{ neg + str(body_atom)}.")
                self._addToFoundednessCheck(pred, arity, [arguments.split(',')], self.g_counter, range(0,arity))
                self.g_counter = chr(ord(self.g_counter) + 1)
            # print rule as it is
            self._outputNodeFormatConform(node)

        self.current_rule_position += 1
        self._reset_after_rule()
        return node

    def visit_Literal(self, node):
        if str(node) != "#false":
            if node.atom.ast_type is clingo.ast.ASTType.SymbolicAtom: # comparisons are reversed by parsing, therefore always using not is sufficient
                if str(node).startswith("not"):
                    self.rule_literals_signums.append(True)
                else:
                    self.rule_literals_signums.append(False)

                #self.rule_literals_signums.append(str(node).startswith("not "))
        self.visit_children(node)
        return node

    def visit_Function(self, node):

        if not self.current_comparison:
            # shows
            if node.name in self.shows:
                self.shows[node.name].add(len(node.arguments))
            else:
                self.shows[node.name] = {len(node.arguments)}

            node = node.update(**self.visit_children(node))
            self.rule_literals.append(node)

        return node

    def visit_Variable(self, node):
        self.rule_is_non_ground = True
        if (str(node) not in self.rule_variables) and str(node) not in self.terms:
            self.rule_variables.append(str(node))

            if str(node) == '_':
                node = node.update(name=f"Anon{self.rule_anonymous_variables}")
                self.rule_anonymous_variables += 1

        return node

    def visit_SymbolicTerm(self, node):
        return node

    def visit_Program(self, node):

        keyword_dict = {}
        keyword_dict["rules"] = "rules"
        keyword_dict["max"] = "max"
        keyword_dict["min"] = "min"
        keyword_dict["count"] = "count"
        keyword_dict["sum"] = "sum"

        self.rules = False
        self.count = False
        self.sum = False
        self.min = False
        self.max = False
        
        if str(node.name) in keyword_dict:
            self.rules = True

        if str(node.name) == "count":
            self.count = True

        if str(node.name) == "sum":
            self.sum = True

        if str(node.name) == "min":
            self.min = True

        if str(node.name) == "max":
            self.max = True

        return node

    def visit_Comparison(self, node):
        # currently implements only terms/variables
        supported_types = [clingo.ast.ASTType.Variable, clingo.ast.ASTType.SymbolicTerm, clingo.ast.ASTType.BinaryOperation, clingo.ast.ASTType.UnaryOperation, clingo.ast.ASTType.Function]

        if len(node.guards) >= 2:
            assert(False) # Not implemented

        left = node.term
        right = node.guards[0].term

        assert(left.ast_type in supported_types)
        assert (right.ast_type in supported_types)

        self.rule_comparisons.append(node)

        self.current_comparison = node

        self.visit_children(node)

        self.current_comparison = None

        return node
    def _generateCombinationInformation(self, h_args, f_vars_needed, c, head):

        interpretation = []  # interpretation-list
        interpretation_incomplete = []  # uncomplete; without removed vars
        nnv = []  # not needed vars
        combs_covered = []  # combinations covered with the (reduced combinations); len=1 when no variable is removed

        if h_args == ['']: # catch head/0
            return interpretation, interpretation_incomplete, [['']],  [str(h_args.index(v)) for v in h_args if v in f_vars_needed or v in self.terms]

        for id, v in enumerate(h_args):
            if v not in f_vars_needed and v not in self.terms:
                nnv.append(v)
            else:
                interpretation_incomplete.append(c[f_vars_needed.index(v)] if v in f_vars_needed else v)
            interpretation.append(c[f_vars_needed.index(v)] if v in f_vars_needed else v)

        head_interpretation = ','.join(interpretation)  # can include vars

        nnv = list(dict.fromkeys(nnv))

        if len(nnv) > 0:
            dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in nnv]
            combs_left_out = [p for p in itertools.product(*dom_list)]  # combinations for vars left out in head
            # create combinations covered for later use in constraints
            for clo in combs_left_out:
                covered = interpretation.copy()
                for id, item in enumerate(covered):
                    if item in nnv:
                        covered[id] = clo[nnv.index(item)]
                if head.name in self.facts and len(h_args) in self.facts[
                    head.name] and ','.join(covered) in self.facts[head.name][len(h_args)]:
                    # no foundation check for this combination, its a fact!
                    continue
                combs_covered.append(covered)
        else:
            if head.name in self.facts and len(h_args) in self.facts[head.name] and head_interpretation in \
                    self.facts[head.name][len(h_args)]:
                # no foundation check for this combination, its a fact!
                return None, None, None, None
            combs_covered.append(interpretation)

        index_vars = [str(h_args.index(v)) for v in h_args if v in f_vars_needed or v in self.terms]

        return interpretation, interpretation_incomplete, combs_covered, index_vars

    def _addToFoundednessCheck(self, pred, arity, combinations, rule, indices):
        indices = tuple(indices)

        for c in combinations:
            c = tuple(c)
            if pred not in self.f:
                self.f[pred] = {}
                self.f[pred][arity] = {}
                self.f[pred][arity][c] = {}
                self.f[pred][arity][c][rule] = {indices}
            elif arity not in self.f[pred]:
                self.f[pred][arity] = {}
                self.f[pred][arity][c] = {}
                self.f[pred][arity][c][rule] = {indices}
            elif c not in self.f[pred][arity]:
                self.f[pred][arity][c] = {}
                self.f[pred][arity][c][rule] = {indices}
            elif rule not in self.f[pred][arity][c]:
                self.f[pred][arity][c][rule] = {indices}
            else:
                self.f[pred][arity][c][rule].add(indices)

    def _outputNodeFormatConform(self, node):
        if str(node.head) == "#false":  # catch constraints and print manually since clingo uses #false
            self.printer.custom_print(f":- {', '.join(str(n) for n in node.body)}.")
        else:
            body_string = f"{', '.join([str(b) for b in node.body])}"

            if node.head.ast_type == clingo.ast.ASTType.Aggregate:
                head_string = f"{str(node.head)}"
            elif node.head.ast_type == clingo.ast.ASTType.Disjunction:
                head_string = "|".join([str(elem) for elem in node.head.elements])
            else:
                head_string = f"{str(node.head).replace(';', ',')}"

            if len(node.body) > 0:  
                self.printer.custom_print(f"{head_string} :- {body_string}.")
            else:
                self.printer.custom_print(f"{head_string}.")



