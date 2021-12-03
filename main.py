import sys
import itertools
import re

import clingo
from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder, Rule
from pprint import pprint

class ClingoApp(object):
    def __init__(self, name):
        self.program_name = name

    def main(self, ctl, files):
        term_transformer = TermTransformer()
        parse_files(files, lambda stm: term_transformer(stm))

        with ProgramBuilder(ctl) as bld:
            transformer = NglpDlpTransformer(bld, term_transformer.terms, term_transformer.facts, term_transformer.ng_heads)
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
                            print(f":- {', '.join([f'{p}({head})'] + rule_sets)}.")

                for t in transformer.terms:
                    print (f"dom({t}).")

                if not term_transformer.shows:
                    for f in transformer.shows.keys():
                        for l in transformer.shows[f]:
                            print (f"#show {f}/{l}.")

class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads):
        self.rules = False
        self.ng = False
        self.bld = bld
        self.terms = terms
        self.facts = facts
        self.ng_heads = ng_heads

        self.cur_anon = 0
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.shows = {}
        self.foundness ={}
        self.f = {}
        self.counter = 0
        self.g_counter = 'A'

    def _reset_after_rule(self):
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.cur_anon = 0
        self.ng = False
        #self.head = None

    def visit_Rule(self, node):
        if not self.rules:
            self._reset_after_rule()
            print (node)
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
                for t in self.terms: # domain
                    disjunction += f"r{self.counter}_{v}({t}), "

                disjunction = disjunction[:-2] + "."
                print (disjunction)

                for t in self.terms:
                    # r1_x(1) :- sat. r1_x(2) :- sat. ...
                    print(f"r{self.counter}_{v}({t}) :- sat.")

            # create combinations
            for f in self.cur_func:
                arguments = re.sub(r'^.*?\(', '', str(f))[:-1].split(',') # all arguments (incl. duplicates / terms)
                var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                h_vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

                combinations = [p for p in itertools.product(self.terms, repeat=len(h_vars))]

                var = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')
                for c in combinations:
                    f_args = ""
                    # vars in atom
                    interpretation = ""
                    for v in var:
                        interpretation += f"r{self.counter}_{v}({c[h_vars.index(v)]}), " if v in self.cur_var else f""
                        f_args += f"{c[h_vars.index(v)]}," if v in self.cur_var else f"{v},"

                    if len(f_args) > 0:
                        f_args = f"{f.name}({f_args[:-1]})"
                    else:
                        f_args = f"{f.name}"

                    print (f"sat_r{self.counter} :- {interpretation}{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else 'not'} {f_args}.")

            # reduce duplicates; track combinations
            sat_per_f = {}
            for f in self.cur_func:
                sat_per_f[f] = []

            # FOUND NEW
            if head is not None:
                # head
                h_args = re.sub(r'^.*?\(', '', str(head))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                h_args_nd = list(dict.fromkeys(h_args)) # arguments (without duplicates / incl. terms)
                h_vars = list(dict.fromkeys(
                    [a for a in h_args if a in self.cur_var]))  # which have to be grounded per combination

                rem = [v for v in self.cur_var if
                       v not in h_vars]  # remaining variables not included in head atom (without facts)

                # GUESS head
                print(f"{{{head} : {','.join(f'dom({v})' for v in h_vars)}}}.")

                guesses_rem = {}
                guesses_comb = {}  # only one guess for each combination of other variables; save those

                # decide which body atom handles rem vars
                for r in rem:
                    guesses_comb[str(r)] = set()
                    max = None
                    vars_not_needed = None
                    for f in self.cur_func:
                        f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)

                        if f != head and r in f_args:
                            f_vars = list(dict.fromkeys([a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination
                            f_vars_needed = [f for f in f_vars if f in h_vars]
                            if vars_not_needed is None or (len(h_vars)-len(f_vars_needed)) > vars_not_needed:
                                max = f
                                vars_not_needed = len(h_vars)-len(f_vars_needed)
                    guesses_rem[r] = max

                # over every body-atom
                for f in self.cur_func:
                    if f != head:
                        f_args = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')  # all arguments (incl. duplicates / terms)
                        f_args_nd = list(dict.fromkeys(f_args))  # arguments (without duplicates / incl. terms)
                        f_vars = list(dict.fromkeys(
                            [a for a in f_args if a in self.cur_var]))  # which have to be grounded per combination

                        f_rem = [v for v in f_vars if
                                 v in rem]  # remaining vars for current function

                        f_vars_needed = [f for f in f_vars if f in h_vars]  # vars needed for foundation of f: if A does not play role in f we can exclude it from combinations

                        combs = [p for p in itertools.product(self.terms, repeat=len(f_vars_needed) + len(f_rem))]

                        for c in combs:
                            interpretation = [] # interpretation-list
                            interpretation_uncomplete = [] # uncomplete; without removed vars
                            nnv = [] # not needed vars
                            combs_covered = [] # combinations covered with the (reduced combinations); len=1 when no variable is removed
                            for id, v in enumerate(h_args):
                                if v not in f_vars_needed and v not in self.terms:
                                    nnv.append(v)
                                else:
                                    interpretation_uncomplete.append(c[f_vars_needed.index(v)] if v in f_vars_needed else v)
                                interpretation.append(c[f_vars_needed.index(v)] if v in f_vars_needed else v)

                            head_interpretation = ','.join(interpretation) # can include vars
                            head_atom_interpretation = head.name + f'({head_interpretation})' if len(var) > 0 else head # can include vars

                            nnv = list(dict.fromkeys(nnv))

                            if len(nnv) > 0:
                                combs_left_out = [p for p in itertools.product(self.terms, repeat=len(nnv))] # combinations for vars left out in head
                                # create combinations covered for later use in constraints
                                for clo in combs_left_out:
                                    covered = interpretation.copy()
                                    for id, item in enumerate(covered):
                                        if item in nnv:
                                            covered[id] = clo[nnv.index(item)]
                                    combs_covered.append(covered)
                            else:
                                combs_covered.append(interpretation)

                            # check if atom is used for rem-guess -> make rem guess
                            combs_covered_tuples = [tuple(cc) for cc in combs_covered]
                            for r in f_rem:
                                if guesses_rem[r] == f:
                                    if len(nnv) == 0:  # removed none
                                        if combs_covered_tuples[0] not in guesses_comb[r]:
                                            print(f"1{{r{self.counter}f_{r}({','.join([r] + interpretation_uncomplete)}): dom({r})}}1 :- {head_atom_interpretation}.")
                                            guesses_comb[str(r)].add(combs_covered_tuples[0])
                                    elif len(nnv) == len(h_vars):  # removed all
                                        if not any(cc in guesses_comb[str(r)] for cc in combs_covered_tuples):
                                            print(f"1{{r{self.counter}f_{r}({','.join([r] + interpretation_uncomplete)}): dom({r})}}1.")
                                            for cc in combs_covered_tuples:
                                                guesses_comb[str(r)].add(cc)
                                    else:  # remove some
                                        if not any(cc in guesses_comb[str(r)] for cc in combs_covered_tuples):
                                            print(f"1{{r{self.counter}f_{r}({','.join([r] + interpretation)}): dom({r})}}1. :- {head_atom_interpretation}, {','.join(f'dom({v})' for v in nnv)}.")
                                            for cc in combs_covered_tuples:
                                                guesses_comb[str(r)].add(cc)

                            index_vars = [str(h_args.index(v)) for v in h_args if v in f_vars_needed or v in self.terms]

                            # generate body for unfound-rule
                            f_args_unf = ""
                            for v in f_args:
                                f_args_unf += f"{c[f_vars_needed.index(v)]}," if v in f_vars_needed else \
                                        (f"{v}," if v in self.terms else f"{c[len(f_vars_needed)+f_rem.index(v)]},")

                            if len(f_args_unf) > 0:
                                f_interpretation = f"{f.name}({f_args_unf[:-1]})"
                            else:
                                f_interpretation = f"{f.name}"

                            f_rem_atoms = [f"r{self.counter}f_{v}({','.join([c[len(f_vars_needed) + f_rem.index(v)]] + (interpretation if len(f_vars_needed) > 0 else interpretation_uncomplete))})" for v in f_args_nd if v in rem]

                            f_interpretation = ('' if self.cur_func_sign[self.cur_func.index(f)] else 'not ') + f_interpretation
                            # r1_unfound(V1,V2) :- p(V1,V2), not f(Z), r1_Z(Z,V1,V2).
                            unfound_atom = f"r{self.counter}_unfound" + (f"_{''.join(index_vars)}" if len(f_vars_needed)<len(h_vars) else "") + (f"({','.join(interpretation_uncomplete)})" if len(interpretation_uncomplete)>0 else "")
                            print(unfound_atom  + f" :- "
                                  f"{', '.join([f_interpretation] + f_rem_atoms)}.")

                            # predicate arity combinations rule indices
                            self._addToFoundednessCheck(head.name, len(h_args), combs_covered, self.counter, index_vars)

        # else: # TODO: update to foundation-check
        #     # foundation needed?
        #     pred = str(node.head).split('(', 1)[0]
        #     arguments = re.sub(r'^.*?\(', '', str(node.head))[:-1].split(',')
        #     arity = len(arguments)
        #     arguments = ','.join(arguments)
        #
        #     if pred in self.ng_heads and arity in self.ng_heads[pred] \
        #             and not (pred in self.facts and arity in self.facts[pred] and arguments in self.facts[pred][arity]):
        #
        #         for body_atom in node.body:
        #             if str(body_atom).startswith("not "):
        #                 neg = ""
        #             else:
        #                 neg = "not "
        #             print(f"r{self.g_counter}_unfound({arguments}) :- "
        #                   f"{ neg + str(body_atom)}.")
        #         self._addToFoundednessCheck(pred, arity, arguments, self.g_counter)
        #         self.g_counter = chr(ord(self.g_counter) + 1)
        #     # print rule as it is
        #     print(node)

        self._reset_after_rule()
        return node

    def visit_Literal(self, node):
        if str(node) != "#false":
            self.cur_func_sign.append(str(node).startswith("not "))
        self.visit_children(node)
        return node

    def visit_Function(self, node):
        # shows
        if node.name in self.shows:
            self.shows[node.name].add(len(re.sub(r'^.*?\(', '', str(node))[:-1].split(',')))
        else:
            self.shows[node.name] = {len(re.sub(r'^.*?\(', '', str(node))[:-1].split(','))}

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
        #print (self.f)

class TermTransformer(Transformer):
    def __init__(self):
        self.terms = []
        self.facts = {}
        self.ng_heads = {}
        self.ng = False
        self.shows = False

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

    def visit_Variable(self, node):
        self.ng = True
        return node

    def visit_Interval(self, node):
        for i in range(int(str(node.left)), int(str(node.right))+1):
            if (str(i) not in self.terms):
                self.terms.append(str(i))
        return node

    def visit_SymbolicTerm(self, node):
        if (str(node) not in self.terms):
            self.terms.append(str(node))
        return node

    def visit_ShowSignature(self, node):
        self.shows = True
        print (node)
        return node


if __name__ == "__main__":
    # no output from clingo itself
    sys.argv.append("--outf=3")
    clingo.clingo_main(ClingoApp(sys.argv[0]), sys.argv[1:])