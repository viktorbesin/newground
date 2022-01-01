import sys
import itertools
import re
import argparse

import clingo
from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder, Rule, ComparisonOperator
from clingo.control import Control
from pprint import pprint

import networkx as nx

class ClingoApp(object):
    def __init__(self, name, no_show=False):
        self.program_name = name
        self.sub_doms = {}
        self.no_show = no_show

    def main(self, ctl, files):
        # read subdomains in #program insts.
        self._readSubDoms(ctl,files)

        term_transformer = TermTransformer(self.sub_doms, self.no_show)
        parse_files(files, lambda stm: term_transformer(stm))

        with ProgramBuilder(ctl) as bld:
            transformer = NglpDlpTransformer(bld, term_transformer.terms, term_transformer.facts, term_transformer.ng_heads, term_transformer.shows, term_transformer.sub_doms)
            parse_files(files, lambda stm: bld.add(transformer(stm)))
            if transformer.counter > 0:
                parse_string(":- not sat.", lambda stm: bld.add(stm))
                print (":- not sat.")
                #parse_string(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.", lambda stm: self.bld.add(stm))
                print(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.")

                for p in transformer.f:
                    for arity in transformer.f[p]:
                        for c in transformer.f[p][arity]:
                            rule_sets = []
                            for r in transformer.f[p][arity][c]:
                                sum_sets = []
                                for subset in transformer.f[p][arity][c][r]:
                                    # print ([c[int(i)] for i in subset])
                                    sum_sets.append(f"1:r{r}_unfound{'_'+''.join(subset) if len(subset) < arity else ''}" + (f"({','.join([c[int(i)] for i in subset])})" if len(subset)>0 else ""))
                                sum_atom = f"#sum {{{'; '.join(sum_sets)}}} >= 1"
                                rule_sets.append(sum_atom)
                            head = ','.join(c)
                            print(f":- {', '.join([f'{p}' +(f'({head})' if len(head)>0 else '')] + rule_sets)}.")

                for t in transformer.terms:
                    print (f"dom({t}).")

                if not self.no_show:
                    if not term_transformer.show:
                        for f in transformer.shows.keys():
                            for l in transformer.shows[f]:
                                print (f"#show {f}/{l}.")

    def _readSubDoms(self, ctl_insts, files):
        #ctl_insts = Control()
        for f in files:
            ctl_insts.load(f)
        ctl_insts.ground([("insts", [])])
        for k in ctl_insts.symbolic_atoms:
            if(str(k.symbol).startswith('_dom_')):
                var = str(k.symbol).split("(", 1)[0]
                atom = re.sub(r'^.*?\(', '', str(k.symbol))[:-1]
                _addToSubdom(self.sub_doms, var, atom)


class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads, shows, sub_doms):
        self.rules = False
        self.ng = False
        self.bld = bld
        self.terms = terms
        self.facts = facts
        self.ng_heads = ng_heads
        self.sub_doms = sub_doms

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
            if str(node.head) == "#false": # catch constraints and print manually since clingo uses #false
                print(f":- {', '.join(str(n) for n in node.body)}.")
            else:
                if len(node.body) > 0:
                    print(f"{str(node.head).replace(';', ',')} :- {', '.join([str(b) for b in node.body])}.")
                else:
                    print(f"{str(node.head).replace(';', ',')}.")
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
                    print (disjunction)

                if v in self.sub_doms:
                    for t in self.sub_doms[v]: # domain
                        # r1_x(1) :- sat. r1_x(2) :- sat. ...
                        print(f"r{self.counter}_{v}({t}) :- sat.")
                else:
                    for t in self.terms: # domain
                        # r1_x(1) :- sat. r1_x(2) :- sat. ...
                        print(f"r{self.counter}_{v}({t}) :- sat.")


            # SAT
            covered_cmp = {} # reduce SAT rules when compare-operators are pre-checked
            for f in self.cur_comp:
                arguments = [str(f.left), str(f.right)] # all arguments (incl. duplicates / terms)
                var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

                dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in vars]
                combinations = [p for p in itertools.product(*dom_list)]

                vars_set = frozenset(vars)
                if vars_set not in covered_cmp:
                    covered_cmp[vars_set] = set()

                for c in combinations:
                    c_varset = tuple([c[vars.index(v)] for v in vars_set])
                    if not self._checkForCoveredSubsets(covered_cmp, list(vars_set),c_varset):  # smaller sets are also possible
                    #if c_varset not in covered_cmp[vars_set]:
                        f_args = ""
                        # vars in atom
                        interpretation = ""
                        for v in var:
                            interpretation += f"r{self.counter}_{v}({c[vars.index(v)]}), " if v in self.cur_var else f""
                            f_args += f"{c[vars.index(v)]}," if v in self.cur_var else f"{v},"
                        c1 = int(c[vars.index(var[0])] if var[0] in vars else var[0])
                        c2 = int(c[vars.index(var[1])] if var[1] in vars else var[1])
                        if not self._compareTerms(f.comparison, c1, c2):
                            covered_cmp[vars_set].add(c_varset)
                            print (f"sat_r{self.counter} :- {interpretation[:-2]}.")

            for f in self.cur_func:
                args_len = len(f.arguments)
                if (args_len == 0):
                    print(
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

                        print (f"sat_r{self.counter} :- {interpretation}{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else 'not '}{f_args}.")

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
                print(f"{{{head}" + (f" : {','.join(f'_dom_{v}({v})' if v in self.sub_doms else f'dom({v})' for v in h_vars)}}}." if h_args_len > 0 else "}."))

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

                for r in rem:
                    g_r[r] = []
                    for n in nx.dfs_postorder_nodes(g, source=r):
                        if n in h_vars:
                            g_r[r].append(n)

                    dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in g_r[r]]
                    needed_combs = [p for p in itertools.product(*dom_list)]
                    for c in needed_combs:
                        head_interpretation = f"{head.name}" + (f"({','.join([c[g_r[r].index(a)] if a in g_r[r] else a  for a in h_args])})" if h_args_len > 0 else "")
                        rem_interpretation = ','.join([r] + [c[g_r[r].index(v)] for v in h_args_nd if v in g_r[r]])
                        doms  = ','.join(f'dom({v})' for v in h_vars if v not in g_r[r])
                        if len(h_vars) == len(g_r[r]):  # removed none
                            print(f"1{{r{self.counter}f_{r}({rem_interpretation}): dom({r})}}1 :- {head_interpretation}.")
                        elif len(g_r[r]) == 0: # removed all
                            print(f"1{{r{self.counter}f_{r}({rem_interpretation}): dom({r})}}1.")
                        else: # removed some
                            print(
                                f"1{{r{self.counter}f_{r}({rem_interpretation}): dom({r})}}1 :- {head_interpretation}, {doms}.")

                covered_cmp = {}
                # for every cmp operator
                for f in self.cur_comp:
                    f_args = [str(f.left), str(f.right)]  # all arguments (incl. duplicates / terms)
                    f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                    f_vars = list(dict.fromkeys(
                        [a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination

                    f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)
                    f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)

                    vars_set = frozenset(f_vars_needed + f_rem)
                    if vars_set not in covered_cmp:
                        covered_cmp[vars_set] = set()

                    combs = [p for p in itertools.product(self.terms, repeat=len(f_vars_needed) + len(f_rem))]
                    for c in combs:
                        c_varset = tuple(
                            [c[f_vars_needed.index(v)] if v in f_vars_needed else c[len(f_vars_needed) + f_rem.index(v)]
                             for v in vars_set])

                        if not self._checkForCoveredSubsets(covered_cmp, list(vars_set), c_varset): # smaller sets are also possible
                        #if c_varset not in covered_cmp[vars_set]:  # smaller sets are also possible
                            interpretation, interpretation_incomplete, combs_covered, index_vars = self._generateCombinationInformation(
                                h_args, f_vars_needed, c, head)
                            if combs_covered is None or combs_covered == []:
                                continue
                            # generate body for unfound-rule
                            f_args_unf_left = f"{c[f_vars_needed.index(f_args[0])]}" if f_args[
                                                                                            0] in f_vars_needed else (
                                f"{f_args[0]}" if f_args[
                                                      0] in self.terms else f"{c[len(f_vars_needed) + f_rem.index(f_args[0])]}")
                            f_args_unf_right = f"{c[f_vars_needed.index(f_args[1])]}" if f_args[
                                                                                             1] in f_vars_needed else (
                                f"{f_args[1]}" if f_args[
                                                      1] in self.terms else f"{c[len(f_vars_needed) + f_rem.index(f_args[1])]}")

                            if not self._compareTerms(f.comparison, f_args_unf_left, f_args_unf_right):
                                f_rem_atoms = [
                                    f"r{self.counter}f_{v}({','.join([c[len(f_vars_needed) + f_rem.index(v)]] + [i for id, i in enumerate(interpretation) if h_args[id] in g_r[v]])})"
                                    for v in f_args_nd if v in rem]

                                covered_cmp[vars_set].add(c_varset)

                                unfound_atom = f"r{self.counter}_unfound" + (
                                    f"_{''.join(index_vars)}" if len(f_vars_needed) < len(h_vars) else "") + (
                                                   f"({','.join(interpretation_incomplete)})" if len(
                                                       interpretation_incomplete) > 0 else "")
                                print(unfound_atom + (
                                    f" :- {', '.join(f_rem_atoms)}" if len(f_rem_atoms) > 0 else "") + ".")
                                #print (f"{h_args_len} | {combs_covered} | {index_vars}")
                                self._addToFoundednessCheck(head.name, h_args_len, combs_covered, self.counter,
                                                            index_vars)

                # over every body-atom
                for f in self.cur_func:
                    if f != head:
                        f_args_len = len(f.arguments)
                        f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                        f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                        f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination

                        f_rem = [v for v in f_vars if v in rem]  # remaining vars for current function (not in head)

                        f_vars_needed = self._getVarsNeeded(h_vars, f_vars, f_rem, g)

                        vars_set = frozenset(f_vars_needed + f_rem)

                        dom_list = [self.sub_doms[v] if v in self.sub_doms else self.terms for v in f_vars_needed+f_rem]
                        combs = [p for p in itertools.product(*dom_list)]

                        for c in combs:
                            c_varset = tuple(
                                [c[f_vars_needed.index(v)] if v in f_vars_needed else c[
                                    len(f_vars_needed) + f_rem.index(v)]
                                 for v in vars_set])
                            if not self._checkForCoveredSubsets(covered_cmp, list(vars_set),c_varset):  # smaller sets are also possible
                            #if vars_set not in covered_cmp or c_varset not in covered_cmp[vars_set]:
                                interpretation, interpretation_incomplete, combs_covered, index_vars = self._generateCombinationInformation(h_args, f_vars_needed, c, head)
                                if combs_covered is None or combs_covered == []:
                                    continue

                                # generate body for unfound-rule
                                if f_args_len > 0:
                                    f_args_unf = ""
                                    for v in f_args:
                                        f_args_unf += f"{c[f_vars_needed.index(v)]}," if v in f_vars_needed else \
                                            (
                                                f"{v}," if v in self.terms else f"{c[len(f_vars_needed) + f_rem.index(v)]},")
                                    f_interpretation = f"{f.name}({f_args_unf[:-1]})"
                                else:
                                    f_interpretation = f"{f.name}"

                                f_rem_atoms = [f"r{self.counter}f_{v}({','.join([c[len(f_vars_needed) + f_rem.index(v)]] + [i for id, i in enumerate(interpretation) if h_args[id] in g_r[v]])})" for v in f_args_nd if v in rem]

                                f_interpretation = ('' if self.cur_func_sign[self.cur_func.index(f)] else 'not ') + f_interpretation
                                # r1_unfound(V1,V2) :- p(V1,V2), not f(Z), r1_Z(Z,V1,V2).
                                unfound_atom = f"r{self.counter}_unfound" + (f"_{''.join(index_vars)}" if len(f_vars_needed)<len(h_vars) else "") + (f"({','.join(interpretation_incomplete)})" if len(interpretation_incomplete)>0 else "")
                                print(unfound_atom  + f" :- "
                                      f"{', '.join([f_interpretation] + f_rem_atoms)}.")

                                # predicate arity combinations rule indices
                                self._addToFoundednessCheck(head.name, h_args_len, combs_covered, self.counter, index_vars)


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
                    print(f"r{self.g_counter}_unfound({arguments}) :- "
                          f"{ neg + str(body_atom)}.")
                self._addToFoundednessCheck(pred, arity, [arguments.split(',')], self.g_counter, range(0,arity))
                self.g_counter = chr(ord(self.g_counter) + 1)
            # print rule as it is
            print(node)

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
        assert(node.left.ast_type is clingo.ast.ASTType.Variable or node.left.ast_type is clingo.ast.ASTType.SymbolicTerm)
        assert (node.right.ast_type is clingo.ast.ASTType.Variable or node.right.ast_type is clingo.ast.ASTType.SymbolicTerm)

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

    def _compareTerms(self, comp, c1, c2):
        if comp is int(clingo.ast.ComparisonOperator.Equal):
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

class TermTransformer(Transformer):
    def __init__(self, sub_doms, no_show=False):
        self.terms = []
        self.sub_doms = sub_doms
        self.facts = {}
        self.ng_heads = {}
        self.ng = False
        self.show = False
        self.shows = {}
        self.current_f = None
        self.no_show = no_show

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
            print (node)
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
    parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = parser.parse_args()
    # no output from clingo itself
    sys.argv.append("--outf=3")
    if args.no_show:
        sys.argv.remove('--no-show')
        clingo.clingo_main(ClingoApp(sys.argv[0], True), sys.argv[1:])
    else:
        clingo.clingo_main(ClingoApp(sys.argv[0]), sys.argv[1:])
