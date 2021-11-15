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
            transformer = NglpDlpTransformer(bld, term_transformer.terms)
            parse_files(files, lambda stm: bld.add(transformer(stm)))
            if transformer.counter > 0:
                parse_string(":- not sat.", lambda stm: bld.add(stm))
                print (":- not sat.")
                #parse_string(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.", lambda stm: self.bld.add(stm))
                print(f"sat :- {','.join([f'sat_r{i}' for i in range(1, transformer.counter+1)])}.")

                # :- not r1_p_f(X,Z), not r2_p_f(X,Z), ... , rk_p_f(X,Z), p(X,Z).
                # {p(D0,D1) : dom(D0),dom(D1)}..
                for p in transformer.foundness:
                    for arity in transformer.foundness[p]:
                        if arity > 0:
                            doms = ','.join(f"dom(D{i})" for i in range (1,arity+1))
                            vars  = ','.join(f'V{i}' for i in range(1, arity+1))
                            print(f"{{{p}({','.join(f'D{i}' for i in range (1,arity+1))}) : {doms}}}.")
                            print(f":- {','.join(f'r{c}_unfound({vars})' for c in transformer.foundness[p][arity])}.")
                        else:
                            print(f"{{{p}}}.")
                            print(f":- {', '.join(f'r{c}_unfound' for c in transformer.foundness[p][arity])}.")
                for t in transformer.terms:
                    print (f"dom({t}).")

                if not term_transformer.shows:
                    for f in transformer.shows.keys():
                        for l in transformer.shows[f]:
                            print (f"#show {f}/{l}.")

class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms):
        self.ng = False        
        self.bld = bld
        self.terms = terms

        self.cur_anon = 0
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.shows = {}
        self.foundness ={}
        self.counter = 0

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
                    atom = ""
                    # vars in atom
                    var = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')
                    for v in var:
                        atom += f"{c[self.cur_var.index(v)]}," if v in self.cur_var else f"{v},"

                    if len(atom) > 0:
                        atom = f"{f.name}({atom[:-1]})"
                    else:
                        atom = f"{f.name}"

                    print (f"sat_r{self.counter} :- {interpretation}{'' if self.cur_func_sign[self.cur_func.index(f)] or f is head else 'not'} {atom}.")


            # FOUND
            if head is not None:
                var = re.sub(r'^.*?\(', '', str(head))[:-1].split(',')
                rem = [v for v in self.cur_var if v not in var] # remaining variables not included in head atom

                for r in rem:
                    # 1{r1_Z(D,X,Y) : dom(D)}1 :- p(X,Y).
                    print (f"1{{r{self.counter}_{r}({','.join([r]+var)}) : dom({r})}}1 :- {head}.")

                for f in self.cur_func:
                    if f != head:
                        # TODO: check if head has arguments
                        f_var = re.sub(r'^.*?\(', '', str(f))[:-1].split(',')
                        f_rem = [f"r{self.counter}_{v}({','.join([v]+var)})" for v in f_var if v in rem]
                        # r1_unfound(V1,V2) :- p(V1,V2), not f(Z), r1_Z(Z,V1,V2).
                        print (f"r{self.counter}_unfound({','.join(var)}) :- "
                               f"{', '.join([str(head)]+[f'not {str(f)}' if not self.cur_func_sign[self.cur_func.index(f)] else str(f)] + f_rem)}.")

                # r1_p_f(X,Z) :- b(X,Y),c(Y,Z), r1_Y_f(Y).
                # print(f"r{self.counter}_{head.name}_f({','.join(var)}) :- "
                #              f"{','.join([f'not {str(f)}' if self.cur_func_sign[self.cur_func.index(f)] else str(f) for f in self.cur_func[1:]])}"
                #              f"{fixed}.")

                # for :- not r1_p_f(X,Z), not r2_p_f(X,Z), ... , rk_p_f(X,Z), p(X,Z).
                if head.name not in self.foundness:
                    self.foundness[head.name] = {}
                    self.foundness[head.name][len(var)] = [self.counter]
                elif len(var) not in self.foundness[head.name]:
                    self.foundness[head.name][len(var)] = [self.counter]
                else:
                    self.foundness[head.name][len(var)].append(self.counter)

            self._reset_after_rule()

        else:
            # print rule as it is
            print(node)
        return node

    def visit_Literal(self, node):
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


# TODO: save facts
class TermTransformer(Transformer):
    def __init__(self):
        self.terms = []
        self.shows = False

    def visit_Interval(self, node):
        print(node)
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