import os 
import sys
import re

import itertools
import argparse
import clingo

from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder, Rule, ComparisonOperator
from clingo.control import Control

from clingox.program import Program, ProgramObserver, Remapping

import networkx as nx

from .comparison_tools import ComparisonTools
from .aggregate_transformer import AggregateMode


class MainTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads, shows, ground_guess, ground, printer, domain, safe_variables_rules, aggregate_mode):
        self.rules = False
        self.count = False
        self.sum = False
        self.min = False
        self.max = False
        
        self.aggregate_mode = aggregate_mode

        self.ng = False
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

        self.cur_anon = 0
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_comp = []
        self.shows = shows
        self.foundness ={}
        self.f = {}
        self.counter = 0
        self.non_ground_rules = {}
        self.g_counter = 'A'

        self.current_comparison = None

        self.unfounded_rules = {}
        self.current_rule_position = 0

    def _reset_after_rule(self):
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_comp = []
        self.cur_anon = 0
        self.ng = False
        #self.head = None

    def _get_domain_values_from_rule_variable(self, rule, variable):
        """ 
            Provided a rule number and a variable in that rule, one gets the domain of this variable.
            If applicable it automatically calculates the intersection of different domains.
        """

        possible_domain_value_name = f"term_rule_{str(rule)}_variable_{str(variable)}"
        if possible_domain_value_name in self.domain:
            return self.domain[possible_domain_value_name]['0']

        if str(rule) not in self.safe_variables_rules:
            return self.domain["0_terms"]

        if str(variable) not in self.safe_variables_rules[str(rule)]:
            return self.domain["0_terms"]

        total_domain = None

        for domain_type in self.safe_variables_rules[str(rule)][str(variable)]:
       
            if domain_type["type"] == "function":
                domain_name = domain_type["name"]
                domain_position = domain_type["position"]

                if domain_name not in self.domain:
                    return self.domain["0_terms"]

                if domain_position not in self.domain[domain_name]:
                    return self.domain["0_terms"]

                cur_domain = self.domain[domain_name][domain_position]

                if total_domain:
                    total_domain = total_domain.intersection(set(cur_domain))
                else:
                    total_domain = set(cur_domain)

        return list(total_domain)

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

        self.visit_children(node)


        # if so: handle grounding
        if self.ng:
            self.non_ground_rules[self.current_rule_position] = self.current_rule_position
            #self.current_rule_position += 1
            if str(node.head) != "#false":
                head = self.cur_func[0]
            else:
                head = None


            self._generate_sat_part(head)

            # FOUND NEW
            if head is not None:
                self._generate_foundedness_part(head)


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
                self.cur_func_sign.append(str(node).startswith("not "))
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
            self.cur_func.append(node)

        return node

    def visit_Variable(self, node):
        self.ng = True
        if (str(node) not in self.cur_var) and str(node) not in self.terms:
            if str(node) == '_':
                node = node.update(name=f"Anon{self.cur_anon}")
                self.cur_anon += 1
            self.cur_var.append(str(node))
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

        self.cur_comp.append(node)

        self.current_comparison = node

        self.visit_children(node)

        self.current_comparison = None

        return node

    def _checkForCoveredSubsets(self, base, current, c_varset):
        for key in base:
            if key.issubset(current):
                c = tuple([c_varset[current.index(p)] for p in list(key)])
                if c in base[key]:
                    return True

        return False

    def _getVarsNeeded(self, h_vars, f_vars, f_rem, g):
        f_vars_needed = [f for f in f_vars if f in h_vars]  # bounded head vars which are needed for foundation
        for r in f_rem:
            for n in nx.dfs_postorder_nodes(g, source=r):
                if n in h_vars and n not in f_vars_needed:
                    f_vars_needed.append(n)
        return f_vars_needed

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

    def _add_atom_to_unfoundedness_check(self, head_string, unfound_atom):

        if head_string not in self.unfounded_rules:
            self.unfounded_rules[head_string] = {}

        if str(self.current_rule_position) not in self.unfounded_rules[head_string]:
            self.unfounded_rules[head_string][str(self.current_rule_position)] = []

        self.unfounded_rules[head_string][str(self.current_rule_position)].append(unfound_atom)


    def _generate_sat_part(self, head):


        self._generate_sat_variable_possibilities()

        covered_subsets = self._generate_sat_comparisons()

        self._generate_sat_functions(head, covered_subsets)


    def _generate_sat_variable_possibilities(self):

        # MOD
        # domaining per rule variable
        for variable in self.cur_var: # variables

            values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 

            disjunction = ""

            for value in values:
                disjunction += f"r{self.current_rule_position}_{variable}({value}) | "

            if len(disjunction) > 0:
                disjunction = disjunction[:-3] + "."
                self.printer.custom_print(disjunction)

            for value in values:
                self.printer.custom_print(f"r{self.current_rule_position}_{variable}({value}) :- sat.")



    def _generate_sat_comparisons(self):

        covered_subsets = {} # reduce SAT rules when compare-operators are pre-checked
        for f in self.cur_comp:

            left = f.term
            assert(len(f.guards) <= 1)
            right = f.guards[0].term
            comparison_operator = f.guards[0].comparison
                            
            symbolic_arguments = ComparisonTools.get_arguments_from_operation(left) + ComparisonTools.get_arguments_from_operation(right)

            arguments = []
            for symbolic_argument in symbolic_arguments:
                arguments.append(str(symbolic_argument))

            var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
            vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination
            dom_list = []
            for variable in vars:
                if str(self.current_rule_position) in self.safe_variables_rules and variable in self.safe_variables_rules[str(self.current_rule_position)]:

                    domain = self._get_domain_values_from_rule_variable(str(self.current_rule_position), variable)
                        
                    dom_list.append(domain)
                else:
                    dom_list.append(self.domain["0_terms"])

            combinations = [p for p in itertools.product(*dom_list)]

            for c in combinations:

                variable_assignments = {}
                
                for variable_index in range(len(vars)):
                    variable = vars[variable_index]
                    value = c[variable_index]

                    variable_assignments[variable] = value

                interpretation_list = []
                for variable in var:
                    if variable in vars:
                        interpretation_list.append(f"r{self.current_rule_position}_{variable}({variable_assignments[variable]})")

                left_eval = ComparisonTools.evaluate_operation(left, variable_assignments)
                right_eval = ComparisonTools.evaluate_operation(right, variable_assignments)

                sint = self.ignore_exception(ValueError)(int)
                left_eval = sint(left_eval)
                right_eval = sint(right_eval)

                safe_checks = left_eval != None and right_eval != None
                evaluation = safe_checks and not ComparisonTools.compareTerms(comparison_operator, int(left_eval), int(right_eval))
                
                if not safe_checks or evaluation:
                    left_instantiation = ComparisonTools.instantiate_operation(left, variable_assignments)
                    right_instantiation = ComparisonTools.instantiate_operation(right, variable_assignments)
                    unfound_comparison = ComparisonTools.comparison_handlings(comparison_operator, left_instantiation, right_instantiation)
                    interpretation = f"{','.join(interpretation_list)}"

                    sat_atom = f"sat_r{self.current_rule_position}"

                    self.printer.custom_print(f"{sat_atom} :- {interpretation}.")

                    if sat_atom not in covered_subsets:
                        covered_subsets[sat_atom] = []

                    covered_subsets[sat_atom].append(interpretation_list)

        return covered_subsets

    def _generate_sat_functions(self, head, covered_subsets):

        for f in self.cur_func:
            args_len = len(f.arguments)
            if (args_len == 0):
                self.printer.custom_print(
                    f"sat_r{self.current_rule_position} :-{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else ' not'} {f}.")
                continue
            arguments = re.sub(r'^.*?\(', '', str(f))[:-1].split(',') # all arguments (incl. duplicates / terms)
            var = list(dict.fromkeys(arguments)) if args_len > 0 else [] # arguments (without duplicates / incl. terms)
            vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) if args_len > 0 else [] # which have to be grounded per combination

            dom_list = []
            for variable in vars:
                values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                dom_list.append(values)

            combinations = [p for p in itertools.product(*dom_list)]

            for c in combinations:
                f_args = ""

                sat_atom = f"sat_r{self.current_rule_position}"

                sat_body_list = []
                sat_body_dict = {}
                for v in var:
                    if v in self.cur_var:
                        body_sat_predicate = f"r{self.current_rule_position}_{v}({c[vars.index(v)]})"
                        sat_body_list.append(body_sat_predicate)
                        sat_body_dict[body_sat_predicate] = body_sat_predicate

                        f_args += f"{c[vars.index(v)]},"
                    else:
                        f_args += f"{v},"

                if len(f_args) > 0:
                    f_args = f"{f.name}({f_args[:-1]})"
                else:
                    f_args = f"{f.name}"

                if sat_atom in covered_subsets:
                    possible_subsets = covered_subsets[sat_atom]
                    found = False

                    for possible_subset in possible_subsets:
                        temp_found = True
                        for possible_subset_predicate in possible_subset:
                            if possible_subset_predicate not in sat_body_dict:
                                temp_found = False
                                break

                        if temp_found == True:
                            found = True
                            break

                    if found == True:
                        continue


                if self.cur_func_sign[self.cur_func.index(f)] or f is head:
                    sat_predicate = f"{f_args}"
                else:
                    sat_predicate = f"not {f_args}"

                if len(sat_body_list) > 0:
                    body_interpretation = ",".join(sat_body_list) + ","
                else:
                    body_interpretation = ""
            
                self.printer.custom_print(f"{sat_atom} :- {body_interpretation}{sat_predicate}.")

    def _generate_foundedness_part(self, head):

        # head
        h_args_len = len(head.arguments)
        h_args = re.sub(r'^.*?\(', '', str(head))[:-1].split(',')  # all arguments (incl. duplicates / terms)
        h_args_nd = list(dict.fromkeys(h_args)) # arguments (without duplicates / incl. terms)
        h_vars = list(dict.fromkeys(
            [a for a in h_args if a in self.cur_var]))  # which have to be grounded per combination


        rem = [v for v in self.cur_var if
               v not in h_vars]  # remaining variables not included in head atom (without facts)

        # GUESS head
        if not self.ground_guess:

            domains = []
            for variable in h_vars:
                domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")
                values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                for value in values:
                    self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{variable}({value}).")

            if len(domains) > 0:
                self.printer.custom_print(f"{{{head} : {','.join(domains)}}}.")
            else:
                self.printer.custom_print(f"{{{head}}}.")

        else:
            
            dom_list = [self._get_domain_values_from_rule_variable(self.current_rule_position, variable) for variable in h_vars]
            combinations = [p for p in itertools.product(*dom_list)]
            h_interpretations = [f"{head.name}({','.join(c[h_vars.index(a)] if a in h_vars else a for a in h_args)})" for c in combinations]
            self.printer.custom_print(f"{{{';'.join(h_interpretations)}}}." if h_args_len > 0 else f"{{{head.name}}}.")

        g_r = {}

        # path checking
        g = nx.Graph()
        for f in self.cur_func:
            f_args_len = len(f.arguments)
            f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
            if f != head and f_args_len > 0:
                f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination
                for v1 in f_vars:
                    for v2 in f_vars:
                        g.add_edge(v1,v2)

        for comp in self.cur_comp:

            left = comp.term
            assert(len(comp.guards) <= 1)
            right = comp.guards[0].term

            unparsed_f_args = ComparisonTools.get_arguments_from_operation(left) + ComparisonTools.get_arguments_from_operation(right)
            f_vars = []
            for unparsed_f_arg in unparsed_f_args:
                f_arg = str(unparsed_f_arg)
                if f_arg in self.cur_var:
                    f_vars.append(f_arg)
            
            for v1 in f_vars:
                for v2 in f_vars:
                    g.add_edge(v1, v2) 

 
        self._generate_foundedness_head(head, rem, g, g_r, h_vars, h_args)

        covered_subsets = self._generate_foundedness_comparisons(head, rem, h_vars, h_args, g)

        self._generate_foundedness_functions(head, rem, h_vars, h_args, g, covered_subsets)


    def _generate_foundedness_head(self, head, rem, g, g_r, h_vars, h_args):
        # ---------------------------------------------
        # REM -> is for the ''remaining'' variables that do not occur in the head
        # The next part is about the introduction of the ''remaining'' variables
        for r in rem:
            g_r[r] = []
            for n in nx.dfs_postorder_nodes(g, source=r):
                if n in h_vars:
                    g_r[r].append(n)

            dom_list = []
            for variable in g_r[r]:
                values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                dom_list.append(values)

            combinations = [p for p in itertools.product(*dom_list)]

           
            for combination in combinations:
                if not self.ground_guess:
                    #head_interpretation = f"{head.name}" + (f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a  for a in h_args])})" if h_args_len > 0 else "")

                    head_tuple_list = []
                    partly_head_tuple_list = []

                    comb_counter = 0
                    for h_arg in h_args:
                        if h_arg in h_vars and h_arg in g_r[r]:
                            head_tuple_list.append(combination[comb_counter])
                            partly_head_tuple_list.append(combination[comb_counter])
                            comb_counter += 1
                        elif h_arg not in h_vars:
                            head_tuple_list.append(h_arg)
                            partly_head_tuple_list.append(h_arg)
                        else:
                            head_tuple_list.append(h_arg)


                    #print(head)
                    head_interpretation = f"{head.name}"

                    #head_tuple_list = [c[index] for index in range(len(c))]

                    if len(head_tuple_list) > 0:
                        head_tuple_interpretation = ','.join(head_tuple_list)
                        head_interpretation += f"({head_tuple_interpretation})"

                    if str(self.current_rule_position) in self.safe_variables_rules and str(r) in self.safe_variables_rules[str(self.current_rule_position)]:

                        values = self._get_domain_values_from_rule_variable(self.current_rule_position, r) 
                        for value in values:
                            self.printer.custom_print(f"domain_rule_{self.current_rule_position}_variable_{r}({value}).")

                        domain_string = f"domain_rule_{self.current_rule_position}_variable_{r}({r})"
                    else:
                        domain_string = f"dom({r})"


                    domains = []
                    for variable in h_vars:
                        domains.append(f"domain_rule_{self.current_rule_position}_variable_{variable}({variable})")

                    if len(domains) > 0:
                        self.printer.custom_print(f"{{{head} : {','.join(domains)}}}.")
                    else:
                        self.printer.custom_print(f"{{{head}}}.")



                    rem_tuple_list = [r] + partly_head_tuple_list
                    rem_tuple_interpretation = ','.join(rem_tuple_list)


                    if len(g_r[r]) == 0:
                        self.printer.custom_print(f"1<={{r{self.current_rule_position}f_{r}({rem_tuple_interpretation}):{domain_string}}}<=1.")
                    else:
                        self.printer.custom_print(f"1<={{r{self.current_rule_position}f_{r}({rem_tuple_interpretation}):{domain_string}}}<=1 :- {head_interpretation}.")

                else:
                    head_interpretation = f"{head.name}" + (
                        f"({','.join([combination[g_r[r].index(a)] if a in g_r[r] else a for a in h_args])})" if h_args_len > 0 else "")
                    rem_interpretation = ','.join([combination[g_r[r].index(v)] for v in h_args_nd if v in g_r[r]])
                    rem_interpretations = ';'.join([f"r{self.current_rule_position}f_{r}({v}{','+rem_interpretation if h_args_len>0 else ''})" for v in (self.sub_doms[r] if r in self.sub_doms else self.terms)])
                    mis_vars  = [v for v in h_vars if v not in g_r[r]]
                    if len(h_vars) == len(g_r[r]):  # removed none
                        self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {head_interpretation}.")
                    elif len(g_r[r]) == 0:  # removed all
                        self.printer.custom_print(f"1{{{rem_interpretations}}}1.")
                    else:  # removed some
                        dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in mis_vars]
                        combinations_2 = [p for p in itertools.product(*dom_list)]
                        h_interpretations = [f"{head.name}({','.join(c2[mis_vars.index(a)] if a in mis_vars else combination[g_r[r].index(a)] for a in h_args)})" for c2 in combinations_2]
                        for hi in h_interpretations:
                            self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {hi}.")



    def _generate_foundedness_comparisons(self, head, rem, h_vars, h_args, g):
        # ---------------------------------------------
        # The next section is about the handling of the comparison operators (foundedness)

        covered_subsets = {}
        # for every cmp operator
        for f in self.cur_comp:

            left = f.term
            assert(len(f.guards) <= 1)
            right = f.guards[0].term
            comparison_operator = f.guards[0].comparison

            symbolic_arguments = ComparisonTools.get_arguments_from_operation(left) + ComparisonTools.get_arguments_from_operation(right)

            arguments = []
            for symbolic_argument in symbolic_arguments:
                arguments.append(str(symbolic_argument))

            f_arguments_nd = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
            f_vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

            f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

            f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)
            combination_variables = f_vars_needed + f_rem

            dom_list = []
            for variable in combination_variables:
                values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                dom_list.append(values)

            combinations = [p for p in itertools.product(*dom_list)]

            #print(f"[INFO] -------> NUMBER OF COMBINATIONS: {len(combinations)}")
            for combination in combinations:

                variable_assignments = {}

                for variable_index in range(len(combination_variables)):
                    variable = combination_variables[variable_index]
                    value = combination[variable_index]

                    variable_assignments[variable] = value


                head_combination, head_combination_list_2, unfound_atom, not_head_counter = self.generate_head_atom(combination, h_vars, h_args, f_vars_needed)

                body_combination = {}

                for f_arg in arguments:
                    if f_arg in h_vars and f_arg in f_vars_needed: # Variables in head
                        body_combination[f_arg] = head_combination[f_arg]
                    elif f_arg in f_vars: # Not in head variables
                        body_combination[f_arg] = (combination[not_head_counter])
                        not_head_counter += 1
                    else: # Static
                        body_combination[f_arg] = f_arg 

                left_eval = ComparisonTools.evaluate_operation(left, variable_assignments)
                right_eval = ComparisonTools.evaluate_operation(right, variable_assignments)

                sint = self.ignore_exception(ValueError)(int)
                left_eval = sint(left_eval)
                right_eval = sint(right_eval)

                safe_checks = left_eval != None and right_eval != None
                evaluation = safe_checks and not ComparisonTools.compareTerms(comparison_operator, int(left_eval), int(right_eval))
            
                if not safe_checks or evaluation:

                    left_instantiation = ComparisonTools.instantiate_operation(left, variable_assignments)
                    right_instantiation = ComparisonTools.instantiate_operation(right, variable_assignments)
                    unfound_comparison = ComparisonTools.comparison_handlings(comparison_operator, left_instantiation, right_instantiation)

                    unfound_body_list = []

                    for v in f_arguments_nd:
                        if v in rem:
                            
                            body_combination_tmp = [body_combination[v]] + head_combination_list_2
                            body_predicate = f"r{self.current_rule_position}f_{v}({','.join(body_combination_tmp)})"
                            unfound_body_list.append(body_predicate)


                    if len(unfound_body_list) > 0:
                        unfound_body = f" {','.join(unfound_body_list)}"
                        unfound_rule = f"{unfound_atom} :- {unfound_body}"
                        unfound_rule += "."

                    else:
                        unfound_rule = f"{unfound_atom}"
                        unfound_rule += "."

                    self.printer.custom_print(unfound_rule)

                    if unfound_atom not in covered_subsets:
                        covered_subsets[unfound_atom] = []

                    covered_subsets[unfound_atom].append(unfound_body_list)

                dom_list_2 = []
                for arg in h_args:
                    if arg in h_vars and arg not in head_combination: 
                        values = self._get_domain_values_from_rule_variable(self.current_rule_position, arg) 
                        dom_list_2.append(values)
                    elif arg in h_vars and arg in head_combination:
                        dom_list_2.append([head_combination[arg]])
                    else:
                        dom_list_2.append([arg])

                combinations_2 = [p for p in itertools.product(*dom_list_2)]

                for combination_2 in combinations_2:

                    if len(head_combination_list_2) > 0:
                        head_string = f"{head.name}({','.join(list(combination_2))})"
                    else:
                        head_string = f"{head.name}"

                    #print(f"{head_string}/{unfound_atom}")
                    self._add_atom_to_unfoundedness_check(head_string, unfound_atom)

        return covered_subsets

    def _generate_foundedness_functions(self, head, rem, h_vars, h_args, g, covered_subsets):
        # -------------------------------------------
        # over every body-atom
        for f in self.cur_func:
            if f != head:

                f_args_len = len(f.arguments)
                f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination

                f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)
                #f_vars_needed = h_vars

                dom_list = []
                for variable in f_vars_needed + f_rem:
                    values = self._get_domain_values_from_rule_variable(self.current_rule_position, variable) 
                    dom_list.append(values)

                combinations = [p for p in itertools.product(*dom_list)]

                for combination in combinations:

                    head_combination, head_combination_list_2, unfound_atom, not_head_counter = self.generate_head_atom(combination, h_vars, h_args, f_vars_needed)

                    # ---------
                    body_combination = {}

                    for f_arg in f_args:
                        if f_arg in h_vars and f_arg in f_vars_needed: # Variables in head
                            body_combination[f_arg] = head_combination[f_arg]
                        elif f_arg in f_vars: # Not in head variables
                            body_combination[f_arg] = (combination[not_head_counter])
                            not_head_counter += 1
                        else: # Static
                            body_combination[f_arg] = f_arg 

                    unfound_body_dict = {}
                    unfound_body_list = []
                    for v in f_args_nd:
                        if v in rem:
                            body_combination_tmp = [body_combination[v]] + head_combination_list_2
                            body_predicate = f"r{self.current_rule_position}f_{v}({','.join(body_combination_tmp)})"
                            unfound_body_list.append(body_predicate)
                            unfound_body_dict[body_predicate] = body_predicate

    
                    if unfound_atom in covered_subsets:
                        possible_subsets = covered_subsets[unfound_atom]
                        found = False

                        for possible_subset in possible_subsets:
                            temp_found = True
                            for possible_subset_predicate in possible_subset:
                                if possible_subset_predicate not in unfound_body_dict:
                                    temp_found = False
                                    break

                            if temp_found == True:
                                found = True
                                break

                        if found == True:
                            continue
                                    
                            
                    unfound_predicate = f"{f.name}"
                    if len(f_args) > 0:
                        unfound_predicate += f"("

                        unfound_predicate_args = []
                        for f_arg in f_args:
                            if f_arg in body_combination:
                                unfound_predicate_args.append(body_combination[f_arg])
                            else:
                                unfound_predicate_args.append(f_arg)

                        unfound_predicate += f"{','.join(unfound_predicate_args)})"

                    if len(unfound_body_list) > 0:
                        unfound_body = f" {','.join(unfound_body_list)},"
                    else:
                        unfound_body = ""

                    sign_adjusted_predicate = "" 
                    if not self.cur_func_sign[self.cur_func.index(f)]: # i.e. a ''positive'' occurence (e.g. q(X) :- p(X) -> p(X) is positive)
                        sign_adjusted_predicate = f"not {unfound_predicate}"
                    else: # i.e. a ''negative'' occurence (e.g. q(X) :- p(X), not p(1). -> p(1) is negative)
                        sign_adjusted_predicate = f"{unfound_predicate}"

                    unfound_rule = f"{unfound_atom} :-{unfound_body} {sign_adjusted_predicate}."

                    self.printer.custom_print(unfound_rule)

                    dom_list_2 = []
                    for arg in h_args:
                        if arg in h_vars and arg not in head_combination: 
                            values = self._get_domain_values_from_rule_variable(self.current_rule_position, arg) 
                            dom_list_2.append(values)
                        elif arg in h_vars and arg in head_combination:
                            dom_list_2.append([head_combination[arg]])
                        else:
                            dom_list_2.append([arg])


                    combinations_2 = [p for p in itertools.product(*dom_list_2)]
                    

                    for combination_2 in combinations_2:

                        
                        if len(list(combination_2)) > 0:
                            head_string = f"{head.name}({','.join(list(combination_2))})"
                        else:
                            head_string = f"{head.name}"

                        self._add_atom_to_unfoundedness_check(head_string, unfound_atom)

    def generate_head_atom(self, combination, h_vars, h_args, f_vars_needed):

        head_combination_list_2 = []
        head_combination = {}

        if len(h_vars) > 0:
            head_combination_list = list(combination[:len(h_vars)])

            head_counter = 0
            for h_arg in h_args:
                if h_arg in h_vars and h_arg in f_vars_needed:
                    head_combination[h_arg] = combination[head_counter]
                    head_counter += 1
                elif h_arg not in h_vars:
                    head_combination[h_arg] = h_arg
                else:   
                    pass

            for h_arg in h_args:
                if h_arg in head_combination:
                    head_combination_list_2.append(head_combination[h_arg])

            if len(head_combination_list_2) > 0:
                unfound_atom = f"r{self.current_rule_position}_unfound({','.join(head_combination_list_2)})"
            else:
                unfound_atom = f"r{self.current_rule_position}_unfound_"

            not_head_counter = head_counter
        elif len(h_args) > 0 and len(h_vars) == 0:

            for h_arg in h_args:
                head_combination_list_2.append(h_arg)
                head_combination[h_arg] = h_arg
                
            unfound_atom = f"r{self.current_rule_position}_unfound({','.join(head_combination_list_2)})"

            not_head_counter = 0

        else:
            unfound_atom = f"r{self.current_rule_position}_unfound"
            not_head_counter = 0
    
        return (head_combination, head_combination_list_2, unfound_atom, not_head_counter)




    def ignore_exception(self, IgnoreException=Exception,DefaultVal=None):
        """ Decorator for ignoring exception from a function
        e.g.   @ignore_exception(DivideByZero)
        e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
        """
        def dec(function):
            def _dec(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except IgnoreException:
                    return DefaultVal
            return _dec
        return dec
