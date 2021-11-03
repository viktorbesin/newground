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
                if not term_transformer.shows:
                    for f in transformer.shows.keys():
                        for l in transformer.shows[f]:
                            parse_string(f"#show {f}/{l}.", lambda stm: bld.add(stm))
                            print (f"#show {f}/{l}.")

        #ctl.ground([("base", [])])

        #ctl.solve()

class NglpDlpTransformer(Transformer):  
    def __init__(self, bld, terms):
        self.ng = False        
        self.bld = bld
        self.terms = terms

        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []
        self.shows = {}
        self.counter = 0

    def _reset_after_rule(self):
        self.cur_var = []
        self.cur_func = []
        self.cur_func_sign = []

    def visit_Rule(self, node):
        # check if AST is non-ground
        self.visit_children(node)
        
        # if so: handle grounding
        if self.ng:
            self.ng = False
            self.counter += 1
            head = self.cur_func[0]

            # MOD
            # domaining per rule variable
            for v in self.cur_var: # variables
                s = ""
                for t in self.terms: # domain
                    s += f"r{self.counter}_{v}({t}), "

                s = s[:-2] + "."
                # parse_string("r1_x(1), r1_x(2), r1_x(3).", lambda stm: self.bld.add(stm))
                parse_string(s, lambda stm: self.bld.add(stm))
                print (s)

                for t in self.terms:
                    # r1_x(1) :- sat. r1_x(2) :- sat. ...
                    parse_string(f"r{self.counter}_{v}({t}) :- sat.", lambda stm: self.bld.add(stm))
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
                        atom += f"{c[self.cur_var.index(v)]},"

                    if len(atom) > 0:
                        atom = f"{f.name}({atom[:-1]})"
                    else:
                        atom = f"{f.name}"

                    parse_string(f"sat_r{self.counter} :- {interpretation}{'' if self.cur_func_sign[self.cur_func.index(f)] or f is head else 'not'} {atom}.", lambda stm: self.bld.add(stm))
                    print (f"sat_r{self.counter} :- {interpretation}{'' if self.cur_func_sign[self.cur_func.index(f)] or f is head else 'not'} {atom}.")

            # parse_string("sat_r1 :- r1_x(1), r1_y(1), r1_z(1), not b(1,1).", lambda stm: self.bld.add(stm))
            # parse_string("sat_r1 :- r1_x(1), r1_y(1), r1_z(1), not c(1,1).", lambda stm: self.bld.add(stm))
            # parse_string("sat_r1 :- r1_x(1), r1_y(1), r1_z(1), p(1,1).", lambda stm: self.bld.add(stm))

            parse_string(f"sat :- sat_r{self.counter}.", lambda stm: self.bld.add(stm))
            print (f"sat :- sat_r{self.counter}.")
            # parse_string("sat: - sat_r1.", lambda stm: self.bld.add(stm))

            # FOUND
            var = re.sub(r'^.*?\(', '', str(head))[:-1].split(',')
            rem = [v for v in self.cur_var if v not in var] # remaining variables not included in head atom

            # for every var not in head -> fix one
            fixed = ""
            for r in rem:
                # # parse_string("1{y(D) : dom(D)}1 :- p(X,Z).", lambda stm: self.bld.add(stm))
                parse_string(f"1{{r{self.counter}_{r}_f(D) : dom(D)}}1 :- {head}.", lambda stm: self.bld.add(stm))
                print (f"1{{r{self.counter}_{r}_f(D) : dom(D)}}1 :- {head}.")
                fixed += f", r{self.counter}_{r}_f({r})"

            # r1_p_f(X,Z) :- b(X,Y),c(Y,Z), r1_Y_f(Y).
            print(f"r{self.counter}_{head.name}_f({','.join(var)}) :- "
                         f"{','.join([f'not {str(f)}' if self.cur_func_sign[self.cur_func.index(f)] else str(f) for f in self.cur_func[1:]])}"
                         f"{fixed}.")
            parse_string(f"r{self.counter}_{head.name}_f({','.join(var)}) :- "
                         f"{','.join([f'not {str(f)}' if self.cur_func_sign[self.cur_func.index(f)] else str(f) for f in self.cur_func[1:]])}"
                         f"{fixed}.", lambda stm: self.bld.add(stm))
            # :- not r1_p_f(X,Z), p(X,Z).
            print(f":- not r{self.counter}_{head.name}_f({','.join(var)}), {str(head)}.")
            parse_string(f":- not r{self.counter}_{head.name}_f({','.join(var)}), {str(head)}.", lambda stm: self.bld.add(stm))

            #I
            # {p(D0,D1) : dom(D0),dom(D1)}..
            doms = []
            for i in range(0, len(var)):
                doms.append(f"D{i}")
            if len(doms) > 0:
                print (f"{{{head.name}({','.join(doms)}) : {','.join([f'dom({d})' for d in doms])}}}.")
                parse_string(f"{{{head.name}({','.join(doms)}) : {','.join([f'dom({d})' for d in doms])}}}.", lambda stm: self.bld.add(stm))
            else:
                print(f"{{{head.name}}}.")
                parse_string(f"{{{head.name}}}.", lambda stm: self.bld.add(stm))

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

        self.cur_func.append(node)
        self.visit_children(node)
        return node

    def visit_Variable(self, node):
        self.ng = True
        if (str(node) not in self.cur_var):
            self.cur_var.append(str(node))
        return node

    def visit_SymbolicTerm(self, node):
        return node


class TermTransformer(Transformer):
    def __init__(self):
        self.terms = []
        self.shows = False

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