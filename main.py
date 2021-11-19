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
                            print(f":- {','.join(f'r{r}_unfound({c})' for r in transformer.f[p][arity][c])}.")

                # :- not r1_p_f(X,Z), not r2_p_f(X,Z), ... , rk_p_f(X,Z), p(X,Z).
                # {p(D0,D1) : dom(D0),dom(D1)}..
                # for p in transformer.foundness:
                #     for arity in transformer.foundness[p]:
                #         if arity > 0:
                #             doms = ','.join(f"dom(D{i})" for i in range (1,arity+1))
                #             vars  = ','.join(f'V{i}' for i in range(1, arity+1))
                #             print(f"{{{p}({','.join(f'D{i}' for i in range (1,arity+1))}) : {doms}}}.")
                #             print(f":- {','.join(f'r{c}_unfound({vars})' for c in transformer.foundness[p][arity])}.")
                #         else:
                #             print(f"{{{p}}}.")
                #             print(f":- {', '.join(f'r{c}_unfound' for c in transformer.foundness[p][arity])}.")
                for t in transformer.terms:
                    print (f"dom({t}).")

                if not term_transformer.shows:
                    for f in transformer.shows.keys():
                        for l in transformer.shows[f]:
                            print (f"#show {f}/{l}.")

class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms, facts, ng_heads):
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

            # SAT per rule
            combinations = [p for p in itertools.product(self.terms, repeat=len(self.cur_var))]
            # for every combination
            for c in combinations:
                # for every atom
                interpretation = ""
                for v in self.cur_var:
                    interpretation += f"r{self.counter}_{v}({c[self.cur_var.index(v)]}), "

                for f in self.cur_func:
                    f_args = ""
                    # vars in atom
                    var = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')
                    for v in var:
                        f_args += f"{c[self.cur_var.index(v)]}," if v in self.cur_var else f"{v},"

                    if len(f_args) > 0:
                        f_args = f"{f.name}({f_args[:-1]})"
                    else:
                        f_args = f"{f.name}"

                    print (f"sat_r{self.counter} :- {interpretation}{'' if (self.cur_func_sign[self.cur_func.index(f)] or f is head) else 'not'} {f_args}.")


            # FOUND
            if head is not None:
                arguments = re.sub(r'^.*?\(', '', str(head))[:-1].split(',') # all arguments (incl. duplicates / terms)
                var = list(dict.fromkeys(arguments)) # arguments (without duplicates / incl. terms)
                actual_vars = list (dict.fromkeys([a for a in arguments if a in self.cur_var])) # which have to be grounded per combination

                rem = [v for v in self.cur_var if v not in var] # remaining variables not included in head atom (without facts)
                head_c = set() # only one guess for each combination of other variables; save those

                # GUESS head
                print(f"{{{head} : {','.join(f'dom({v})' for v in actual_vars)}}}.")

                combinations = [p for p in itertools.product(self.terms, repeat=len(actual_vars)+len(rem))]
                for c in combinations:
                    interpretation = []
                    # TODO: check for terms here
                    for v in arguments:
                        interpretation.append(c[actual_vars.index(v)] if v in actual_vars else v)
                    head_interpretation = ','.join(interpretation)
                    head_atom_interpretation = head.name + f'({head_interpretation})' if len(var) > 0 else head

                    if head.name in self.facts and len(arguments) in self.facts[head.name] and head_interpretation in self.facts[head.name][len(arguments)]:
                        # no foundation check for this combination, its a fact!
                        continue

                    if head_interpretation not in head_c:
                        head_c.add(head_interpretation)
                        for r in rem:
                            # 1{r1_Z(D,X,Y) : dom(D)}1 :- p(X,Y).
                            print(f"1{{r{self.counter}_{r}({','.join([r] + interpretation)}): dom({r})}}1 :- {head_atom_interpretation}.")

                    for f in self.cur_func: # all predicates
                        if f != head: # only for the body
                            # TODO: check if head has arguments
                            f_var = re.sub(r'^.*?\(', '', str(f))[:-1].split(',') # body-pred vars; can include terms
                            f_rem = [f"r{self.counter}_{v}({','.join([c[len(actual_vars)+rem.index(v)]] + interpretation)})" for v in f_var if v in rem]
                            f_args = ""
                            for v in f_var:
                                f_args += f"{c[self.cur_var.index(v)]}," if v in actual_vars else \
                                    (f"{v}," if v in self.terms else f"{c[len(actual_vars)+rem.index(v)]},")

                            if len(f_args) > 0:
                                f_interpretation = f"{f.name}({f_args[:-1]})"
                            else:
                                f_interpretation = f"{f.name}"

                            f_interpretation = ('' if self.cur_func_sign[self.cur_func.index(f)] else 'not ') + f_interpretation
                            # r1_unfound(V1,V2) :- p(V1,V2), not f(Z), r1_Z(Z,V1,V2).
                            print(f"r{self.counter}_unfound({','.join(interpretation)}) :- "
                                  f"{', '.join([head_atom_interpretation] + [f_interpretation] + f_rem)}.")

                    self._addToFoundednessCheck(head.name, len(arguments), head_interpretation, self.counter)

            self._reset_after_rule()

        else:
            # foundation needed?
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
                self._addToFoundednessCheck(pred, arity, arguments, self.g_counter)
                self.g_counter = chr(ord(self.g_counter) + 1)
            # print rule as it is
            print(node)
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
    
    def _addToFoundednessCheck(self, pred, arity, combination, rule):
        if pred not in self.f:
            self.f[pred] = {}
            self.f[pred][arity] = {}
            self.f[pred][arity][combination] = {rule}
        elif arity not in self.f[pred]:
            self.f[pred][arity] = {}
            self.f[pred][arity][combination] = {rule}
        elif combination not in self.f[pred][arity]:
            self.f[pred][arity][combination] = {rule}
        else:
            self.f[pred][arity][combination].add(rule)

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
        if self.ng and str(node.head) != "#false":
            # save pred and arity for later use
            if pred not in self.ng_heads:
                self.ng_heads[pred] = {arity}
            else:
                self.ng_heads[pred].add(arity)
            self.ng = False
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