import sys
import itertools
import re
import argparse

import clingo
from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder, Rule, ComparisonOperator
from clingo.control import Control
from pprint import pprint
from clingox.program import Program, ProgramObserver, Remapping

import networkx as nx

class DefaultOutputPrinter:

    def custom_print(self, string):
        print(string)


class ClingoApp(object):
    def __init__(self, name, no_show=False, ground_guess=False, ground=False, output_printer = None):
        self.program_name = name
        self.sub_doms = {}
        self.no_show = no_show
        self.ground_guess = ground_guess
        self.ground = ground

        if not output_printer:
            self.printer = DefaultOutputPrinter()
        else:
            self.printer = output_printer

        self.prg = Program()

    def main(self, ctl, inputs):

        combined_inputs = '\n'.join(inputs)

        ctl_insts = Control()
        ctl_insts.register_observer(ProgramObserver(self.prg))
        # read subdomains in #program insts.
        self._readSubDoms(ctl_insts,combined_inputs)
        if self.ground:
            self.printer.custom_print(self.prg)

        term_transformer = TermTransformer(self.sub_doms, self.printer, self.no_show)
        #parse_files(inputs, lambda stm: term_transformer(stm))
        parse_string(combined_inputs, lambda stm: term_transformer(stm))

        with ProgramBuilder(ctl) as bld:
            transformer = NglpDlpTransformer(bld, term_transformer.terms, term_transformer.facts, term_transformer.ng_heads, term_transformer.shows, term_transformer.sub_doms, self.ground_guess, self.ground, self.printer)
            #parse_files(combined_inputs, lambda stm: bld.add(transformer(stm)))
            parse_string(combined_inputs, lambda stm: bld.add(transformer(stm)))
            if transformer.counter > 0:
                parse_string(":- not sat.", lambda stm: bld.add(stm))
                self.printer.custom_print(":- not sat.")
                #parse_string(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.", lambda stm: self.bld.add(stm))
                self.printer.custom_print(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.")

                #print(transformer.unfounded_rules)

                for key in transformer.unfounded_rules.keys():
                    unfounded_rules_list = transformer.unfounded_rules[key]

                    sum_list = []
                    for index in range(len(unfounded_rules_list)):
                        unfounded_rule = unfounded_rules_list[index]

                        sum_list.append(f"1,{index} : {unfounded_rule}")


                    self.printer.custom_print(f":- {key}, #sum{{{'; '.join(sum_list)}}} >=1.")
                

                if not self.ground_guess:
                    for t in transformer.terms:
                        self.printer.custom_print(f"dom({t}).")

                if not self.no_show:
                    if not term_transformer.show:
                        for f in transformer.shows.keys():
                            for l in transformer.shows[f]:
                                self.printer.custom_print(f"#show {f}/{l}.")

    def _readSubDoms(self, ctl_insts, combined_inputs):
        #ctl_insts = Control()
      
        """ 
        for f in files:
            ctl_insts.load(f)
        """
        
        """ 
        ctl_insts.add("base", [], combined_inputs)
            
        ctl_insts.ground([("base", []), ("insts", [])])
        for k in ctl_insts.symbolic_atoms:
            if(str(k.symbol).startswith('_dom_')):
                var = str(k.symbol).split("(", 1)[0]
                atom = re.sub(r'^.*?\(', '', str(k.symbol))[:-1]
                _addToSubdom(self.sub_doms, var, atom)

        """
        pass


class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads, shows, sub_doms, ground_guess, ground, printer):
        self.rules = False
        self.ng = False
        self.bld = bld
        self.terms = terms
        self.facts = facts
        self.ng_heads = ng_heads
        self.sub_doms = sub_doms
        self.ground_guess = ground_guess
        self.ground = ground
        self.printer = printer

        self.cur_anon = 0
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_comp = []
        self.shows = shows
        self.foundness ={}
        self.f = {}
        self.counter = 0
        self.g_counter = 'A'

        self.unfounded_rules = {}

    def _reset_after_rule(self):
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_comp = []
        self.cur_anon = 0
        self.ng = False
        #self.head = None

    def visit_Rule(self, node):

        if not self.rules:
            self._reset_after_rule()
            if not self.ground:
                self._outputNodeFormatConform(node)
            return node

        # check if AST is non-ground
        self.visit_children(node)

        # if so: handle grounding
        if self.ng:
            self.counter += 1
            if str(node.head) != "#false":
                head = self.cur_func[0]
            else:
                head = None

            # MOD
            # domaining per rule variable
            for v in self.cur_var: # variables
                disjunction = ""
                if v in self.sub_doms:
                    for t in self.sub_doms[v]: # domain
                        disjunction += f"r{self.counter}_{v}({t}) | "
                else:
                    for t in self.terms: # domain
                        disjunction += f"r{self.counter}_{v}({t}) | "
                if len(disjunction) > 0:
                    disjunction = disjunction[:-3] + "."
                    self.printer.custom_print(disjunction)

                if v in self.sub_doms:
                    for t in self.sub_doms[v]: # domain
                        # r1_x(1) :- sat. r1_x(2) :- sat. ...
                        self.printer.custom_print(f"r{self.counter}_{v}({t}) :- sat.")
                else:
                    for t in self.terms: # domain
                        # r1_x(1) :- sat. r1_x(2) :- sat. ...
                        self.printer.custom_print(f"r{self.counter}_{v}({t}) :- sat.")


            # ----------------------------
            # SAT
            # SAT for comparison operators

            covered_cmp = {} # reduce SAT rules when compare-operators are pre-checked
            for f in self.cur_comp:
                                
                symbolic_arguments = self._get_arguments_from_operation(f.left) + self._get_arguments_from_operation(f.right)

                arguments = []
                for symbolic_argument in symbolic_arguments:
                    arguments.append(str(symbolic_argument))

                var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

                dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in vars]
                combinations = [p for p in itertools.product(*dom_list)]

                vars_set = frozenset(vars)
                if vars_set not in covered_cmp:
                    covered_cmp[vars_set] = set()

                for c in combinations:
    
                    variable_assignments = {}
                    
                    for variable_index in range(len(vars)):
                        variable = vars[variable_index]
                        value = c[variable_index]

                        variable_assignments[variable] = value

                    interpretation = ""
                    for variable in var:
                        if variable in vars:
                            interpretation += f"r{self.counter}_{variable}({variable_assignments[variable]}),"

                    left = self._instantiate_operation(f.left, variable_assignments)
                    right = self._instantiate_operation(f.right, variable_assignments)
                    comparison = self._comparison_handlings(f.comparison, left, right)

                    interpretation += f" not {comparison}"

                    self.printer.custom_print(f"sat_r{self.counter} :- {interpretation}.")


            for f in self.cur_func:
                args_len = len(f.arguments)
                if (args_len == 0):
                    self.printer.custom_print(
                        f"sat_r{self.counter} :-{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else ' not'} {f}.")
                    continue
                arguments = re.sub(r'^.*?\(', '', str(f))[:-1].split(',') # all arguments (incl. duplicates / terms)
                var = list(dict.fromkeys(arguments)) if args_len > 0 else [] # arguments (without duplicates / incl. terms)
                vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) if args_len > 0 else [] # which have to be grounded per combination

                dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in vars]
                combinations = [p for p in itertools.product(*dom_list)]
                vars_set = frozenset(vars)

                for c in combinations:
                    c_varset = tuple([c[vars.index(v)] for v in vars_set])
                    if not self._checkForCoveredSubsets(covered_cmp, list(vars_set), c_varset):  # smaller sets are also possible
                    #if vars_set not in covered_cmp or c_varset not in covered_cmp[vars_set]:
                        f_args = ""
                        # vars in atom
                        interpretation = ""
                        for v in var:
                            interpretation += f"r{self.counter}_{v}({c[vars.index(v)]}), " if v in self.cur_var else f""
                            f_args += f"{c[vars.index(v)]}," if v in self.cur_var else f"{v},"

                        if len(f_args) > 0:
                            f_args = f"{f.name}({f_args[:-1]})"
                        else:
                            f_args = f"{f.name}"

                        self.printer.custom_print(f"sat_r{self.counter} :- {interpretation}{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else 'not '}{f_args}.")

            # reduce duplicates; track combinations
            sat_per_f = {}
            for f in self.cur_func:
                sat_per_f[f] = []

            # FOUND NEW
            if head is not None:
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
                    self.printer.custom_print(f"{{{head}" + (f" : {','.join(f'_dom_{v}({v})' if v in self.sub_doms else f'dom({v})' for v in h_vars)}}}." if h_args_len > 0 else "}."))
                else:
                    dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in h_vars]
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
                    g.add_edge(str(comp.left), str(comp.left))

                # ---------------------------------------------
                # REM -> is for the ''remaining'' variables that do not occur in the head
                # The next part is about the introduction of the ''remaining'' variables
                for r in rem:
                    g_r[r] = []
                    for n in nx.dfs_postorder_nodes(g, source=r):
                        if n in h_vars:
                            g_r[r].append(n)

                    dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in g_r[r]]
                    #needed_combs = [p for p in itertools.product(*dom_list)]

                    iter_list = []
                    for i in range(len(h_vars)):
                        iter_list.append(self.terms)


                    combs = [p for p in itertools.product(*iter_list)]


                    for c in combs:
                        if not self.ground_guess:
                            #head_interpretation = f"{head.name}" + (f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a  for a in h_args])})" if h_args_len > 0 else "")

                            head_tuple_list = []
        
                            comb_counter = 0
                            for h_arg in h_args:
                                if h_arg in h_vars:
                                    head_tuple_list.append(c[comb_counter])
                                    comb_counter += 1
                                else:
                                    head_tuple_list.append(h_arg)


                            head_interpretation = f"{head.name}"
                            #head_tuple_list = [c[index] for index in range(len(c))]
                            head_tuple_interpretation = ','.join(head_tuple_list)

                            if len(c) > 0:
                                head_interpretation += f"({head_tuple_interpretation})"

                            #rem_interpretation = ','.join([r] + [c[g_r[r].index(v)] for v in h_args_nd if v in g_r[r]])
                            #doms  = ','.join(f'dom({v})' for v in h_vars if v not in g_r[r])

                            rem_tuple_list = [r] + head_tuple_list
                            rem_tuple_interpretation = ','.join(rem_tuple_list)

                            self.printer.custom_print(f"1<={{r{self.counter}f_{r}({rem_tuple_interpretation}):dom({r})}}<=1 :- {head_interpretation}.")

                        else:
                            head_interpretation = f"{head.name}" + (
                                f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a for a in h_args])})" if h_args_len > 0 else "")
                            rem_interpretation = ','.join([c[g_r[r].index(v)] for v in h_args_nd if v in g_r[r]])
                            rem_interpretations = ';'.join([f"r{self.counter}f_{r}({v}{','+rem_interpretation if h_args_len>0 else ''})" for v in (self.sub_doms[r] if r in self.sub_doms else self.terms)])
                            mis_vars  = [v for v in h_vars if v not in g_r[r]]
                            if len(h_vars) == len(g_r[r]):  # removed none
                                self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {head_interpretation}.")
                            elif len(g_r[r]) == 0:  # removed all
                                self.printer.custom_print(f"1{{{rem_interpretations}}}1.")
                            else:  # removed some
                                dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in mis_vars]
                                combinations = [p for p in itertools.product(*dom_list)]
                                h_interpretations = [f"{head.name}({','.join(c2[mis_vars.index(a)] if a in mis_vars else c[g_r[r].index(a)] for a in h_args)})" for c2 in combinations]
                                for hi in h_interpretations:
                                    self.printer.custom_print(f"1{{{rem_interpretations}}}1 :- {hi}.")

                # ---------------------------------------------
                # The next section is about the handling of the comparison operators
                covered_cmp = {}
                # for every cmp operator
                for f in self.cur_comp:

                    symbolic_arguments = self._get_arguments_from_operation(f.left) + self._get_arguments_from_operation(f.right)

                    arguments = []
                    for symbolic_argument in symbolic_arguments:
                        arguments.append(str(symbolic_argument))

                    f_arguments_nd = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                    f_vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

                    f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                    f_vars_needed = h_vars

                    vars_set = frozenset(f_vars_needed + f_rem)

                    dom_list = []

                    for v in f_vars_needed + f_rem:
                        if v in self.sub_doms:
                            dom_list.append(self.sub_doms[v])
                        else:
                            dom_list.append(self.terms)
                        

                    #dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in f_vars_needed+f_rem]
                    combs = [p for p in itertools.product(*dom_list)]

                    for c in combs:
     
                        variable_assignments = {}

                        for variable_index in range(len(f_vars)):
                            variable = f_vars[variable_index]
                            value = c[variable_index]

                            variable_assignments[variable] = value

                        head_combination_list = list(c[:len(h_vars)])

                        head_combination = {}

                        for h_arg in h_args:
                            if h_arg in h_vars:
                                head_combination[h_arg] = variable_assignments[h_arg]
                            else:
                                head_combination[h_arg] = h_arg

                        head_combination_list_2 = []
                        for h_arg in h_args:
                            head_combination_list_2.append(head_combination[h_arg])

                        unfound_atom = f"r{self.counter}_unfound({','.join(head_combination_list_2)})"

                        body_combination = {}

                        for f_arg in arguments:
                            if f_arg in f_vars: # Is a variable
                                body_combination[f_arg] = variable_assignments[f_arg]
                            else: # Static
                                body_combination[f_arg] = f_arg 

                        left = self._instantiate_operation(f.left, variable_assignments)
                        right = self._instantiate_operation(f.right, variable_assignments)

                        unfound_comparison = self._comparison_handlings(f.comparison, left, right)

                        unfound_body_list = []
                        for v in f_arguments_nd:
                            if v in rem:

                                #if not self._compareTerms(f.comparison, f_args_unf_left, f_args_unf_right):
                                
                                body_combination_tmp = [body_combination[v]] + head_combination_list_2
                                body_predicate = f"r{self.counter}f_{v}({','.join(body_combination_tmp)})"
                                unfound_body_list.append(body_predicate)


                        if len(unfound_body_list) > 0:
                            unfound_body = f" {','.join(unfound_body_list)},"
                        else:
                            unfound_body = ""

                        unfound_rule = f"{unfound_atom} :-{unfound_body} not {unfound_comparison}."
                        self.printer.custom_print(unfound_rule)

                        if len(head_combination_list_2) > 0:
                            head_string = f"{head.name}({','.join(head_combination_list_2)})"
                        else:
                            head_string = f"{head.name}"


                        if head_string not in self.unfounded_rules:
                            self.unfounded_rules[head_string] = []

                        self.unfounded_rules[head_string].append(unfound_atom)


                # -------------------------------------------
                # over every body-atom
                for f in self.cur_func:
                    if f != head:

                        

                        f_args_len = len(f.arguments)
                        f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                        f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                        f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination

                        f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                        #f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)
                        f_vars_needed = h_vars

                        vars_set = frozenset(f_vars_needed + f_rem)

                        dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in f_vars_needed+f_rem]
                        combs = [p for p in itertools.product(*dom_list)]

                        for c in combs:
                            head_combination_list = list(c[:len(h_vars)])

                            head_combination = {}

                            head_counter = 0
                            for h_arg in h_args:
                                if h_arg in h_vars:
                                    head_combination[h_arg] = c[head_counter]
                                    head_counter += 1
                                else:
                                    head_combination[h_arg] = h_arg

                            head_combination_list_2 = []
                            for h_arg in h_args:
                                head_combination_list_2.append(head_combination[h_arg])

                            unfound_atom = f"r{self.counter}_unfound({','.join(head_combination_list_2)})"


                            # ---------
                            body_combination = {}

                            not_head_counter = len(h_vars)
                            for f_arg in f_args:
                                if f_arg in h_vars: # Variables in head
                                    index_head = h_vars.index(f_arg)
                                    body_combination[f_arg] = (c[index_head])
                                elif f_arg in f_vars: # Not in head variables
                                    body_combination[f_arg] = (c[not_head_counter])
                                    not_head_counter += 1
                                else: # Static
                                    body_combination[f_arg] = f_arg 
    

                            unfound_body_list = []
                            for v in f_args_nd:
                                if v in rem:
                                    body_combination_tmp = [body_combination[v]] + head_combination_list_2
                                    body_predicate = f"r{self.counter}f_{v}({','.join(body_combination_tmp)})"
                                    unfound_body_list.append(body_predicate)

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


                            if len(head_combination_list_2) > 0:
                                head_string = f"{head.name}({','.join(head_combination_list_2)})"
                            else:
                                head_string = f"{head.name}"


                            if head_string not in self.unfounded_rules:
                                self.unfounded_rules[head_string] = []

                            self.unfounded_rules[head_string].append(unfound_atom)

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

        self._reset_after_rule()
        return node

    def visit_Literal(self, node):
        if str(node) != "#false":
            if node.atom.ast_type is clingo.ast.ASTType.SymbolicAtom: # comparisons are reversed by parsing, therefore always using not is sufficient
                self.cur_func_sign.append(str(node).startswith("not "))
        self.visit_children(node)
        return node

    def visit_Function(self, node):
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

        if node.name == 'rules':
            self.rules = True
        else:
            self.rules = False

        return node

    def visit_Comparison(self, node):
        # currently implements only terms/variables
        supported_types = [clingo.ast.ASTType.Variable, clingo.ast.ASTType.SymbolicTerm, clingo.ast.ASTType.BinaryOperation, clingo.ast.ASTType.UnaryOperation]

        assert(node.left.ast_type in supported_types)
        assert (node.right.ast_type in supported_types)

        self.cur_comp.append(node)
        self.visit_children(node)
        return node

    def _getCompOperator(self, comp):
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

    def _comparison_handlings(self, comp, c1, c2):
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


    def _compareTerms(self, comp, c1, c2):
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


    def _get_arguments_from_operation(self, root):
        """
            Performs a tree traversal of an operation (e.g. X+Y -> first ''+'', then ''X'' and lasylt ''Y'' -> then combines together)
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            return self._get_arguments_from_operation(root.left) + self._get_arguments_from_operation(root.right)

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            return self._get_arguments_from_operation(root.argument)

        elif root.ast_type is clingo.ast.ASTType.Variable or root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return [root]
        else:
            assert(False) # not implemented

    def _instantiate_operation(self, root, variable_assignments):
        """
            Instantiates a operation and returns a string
        """

        if root.ast_type is clingo.ast.ASTType.BinaryOperation:
            string_rep = self._get_binary_operator_type_as_string(root.operator_type)
    
            return "(" + self._instantiate_operation(root.left, variable_assignments) + string_rep + self._instantiate_operation(root.right, variable_assignments) + ")"

        elif root.ast_type is clingo.ast.ASTType.UnaryOperation:
            string_rep = self._get_unary_operator_type_as_string(root.operator_type)

            if string_rep != "ABSOLUTE":
                return "(" + string_rep + self._instantiate_operation(root.argument, variable_assignments) + ")"
            elif string_rep == "ABSOLUTE":
                return "(|" + self._instantiate_operation(root.argument, variable_assignments) + "|)"

        elif root.ast_type is clingo.ast.ASTType.Variable:
            variable_string = str(root)
            return variable_assignments[variable_string]

        elif root.ast_type is clingo.ast.ASTType.SymbolicTerm:
            return str(root)

        else:
            assert(False) # not implemented

    def _get_unary_operator_type_as_string(self, operator_type):
        if operator_type == 0:
            return "-"
        elif operator_type == 1:
            return "~"
        elif operator_type == 2: # Absolute, i.e. |X| needs special handling
            return "ABSOLUTE"
        else:
            print(f"[NOT-IMPLEMENTED] - Unary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented

    def _get_binary_operator_type_as_string(self, operator_type):
        if operator_type == 0:
            return "^"
        elif operator_type == 1:
            return "?"
        elif operator_type == 2:
            return "&"
        elif operator_type == 3:
            return "+"
        elif operator_type == 4:
            return "-"
        elif operator_type == 5:
            return "*"
        elif operator_type == 6:
            return "/"
        elif operator_type == 7:
            return "\\"
        elif operator_type == 8:
            return "**"
        else:
            print(f"[NOT-IMPLEMENTED] - Binary operator type '{operator_type}' is not implemented!")
            assert(False) # not implemented


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
            if len(node.body) > 0:
                if (str(node.head).startswith('{')):
                    self.printer.custom_print(f"{str(node.head)} :- {', '.join([str(b) for b in node.body])}.")
                else:
                    self.printer.custom_print(f"{str(node.head).replace(';', ',')} :- {', '.join([str(b) for b in node.body])}.")
            else:
                if (str(node.head).startswith('{')):
                    self.printer.custom_print(f"{str(node.head)}.")
                else:
                    self.printer.custom_print(f"{str(node.head).replace(';', ',')}.")

class TermTransformer(Transformer):
    def __init__(self, sub_doms, printer, no_show=False):
        self.terms = []
        self.sub_doms = sub_doms
        self.facts = {}
        self.ng_heads = {}
        self.ng = False
        self.show = False
        self.shows = {}
        self.current_f = None
        self.no_show = no_show
        self.printer = printer

    def visit_Rule(self, node):
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
        return node

    def visit_Function(self, node):
        self.current_f = str(node).split("(", 1)[0] if len(node.arguments) > 0 else node
        # shows
        #if not str(node.name).startswith('_dom_'):
        if node.name in self.shows:
            self.shows[node.name].add(len(node.arguments))
        else:
            self.shows[node.name] = {len(node.arguments)}
        self.visit_children(node)
        return node

    def visit_Variable(self, node):
        self.ng = True
        return node

    def visit_Interval(self, node):
        for i in range(int(str(node.left)), int(str(node.right))+1):
            if (str(i) not in self.terms):
                self.terms.append(str(i))
            _addToSubdom(self.sub_doms, self.current_f, str(i))
        return node

    def visit_SymbolicTerm(self, node):
        if (str(node) not in self.terms):
            self.terms.append(str(node))
        _addToSubdom(self.sub_doms, self.current_f, str(node))
        return node

    def visit_ShowSignature(self, node):
        self.show = True
        if not self.no_show:
            self.printer.custom_print(node)
        return node

def _addToSubdom(sub_doms, var, value):
    if var.startswith('_dom_'):
        var = var[5:]
    else:
        return

    if var not in sub_doms:
        sub_doms[var] = []
        sub_doms[var].append(value)
    elif value not in sub_doms[var]:
        sub_doms[var].append(value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='newground', usage='%(prog)s [files]')
    parser.add_argument('--no-show', action='store_true', help='Do not print #show-statements to avoid compatibility issues. ')
    parser.add_argument('--ground-guess', action='store_true',
                        help='Additionally ground guesses which results in (fully) grounded output. ')
    parser.add_argument('--ground', action='store_true',
                        help='Output program fully grounded. ')
    parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = parser.parse_args()
    # no output from clingo itself
    #sys.argv.append("--outf=3")
    no_show = False
    ground_guess = False
    ground = False
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


    contents = ""
    for f in sys.argv[1:]:
        contents += open(f, "r").read()

    #clingo.clingo_main(ClingoApp(sys.argv[0], no_show, ground_guess, ground), sys.argv[1:])
    newground = ClingoApp(sys.argv[0], no_show, ground_guess, ground)
    newground.main(clingo.Control(), [contents])


