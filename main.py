import sys
import clingo
from clingo.ast import Transformer, Variable, parse_files, parse_string, ProgramBuilder
from pprint import pprint

class ClingoApp(object):
    def __init__(self, name):
        self.program_name = name

    def main(self, ctl, files):

        with ProgramBuilder(ctl) as bld:
        
            transformer = NglpDlpTransformer(bld)
            parse_files(files, lambda stm: bld.add(transformer(stm)))

        #for f in files:
            #ctl.load(f)
        #if not files:
            #ctl.load("-")
            
        ctl.ground([("base", [])])
        ctl.solve()

class NglpDlpTransformer(Transformer):  
    def __init__(self, bld):
        self.ng = False        
        self.bld = bld

    def visit_Rule(self, node): 
        # check if AST is non-grozund
        self.visit_children(node)
        
        # if so: handle grounding
        if self.ng:
            self.ng = False
            # MOD
            parse_string("r1_x(1), r1_x(2), r1_x(3).", lambda stm: self.bld.add(stm))
            

        return node

    def visit_Variable(self, node):
        self.ng = True
        return node


class Application(object):
    def _read(self, path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as file_:
            return file_.read()


    def main(self, clingo_control, files):
        if not files:
            files = ["-"]

        control = clingo.Control()

        for path in files:
            control.add("base", [], self._read(path))


        control.ground([('base', [])])

        print("------------------------------------------------------------")
        print("   Grounded Program")
        print("------------------------------------------------------------")
        #print(control)
        print("-------------------------------------------------------------")
        #print(control.solve(on_model=print))




if __name__ == "__main__":
    clingo.clingo_main(ClingoApp(sys.argv[0]), sys.argv[1:])
