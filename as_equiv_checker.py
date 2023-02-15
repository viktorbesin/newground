import os
import sys
import argparse

import clingo

from newground import ClingoApp, DefaultOutputPrinter

def block_print():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

class CustomOutputPrinter(DefaultOutputPrinter):

    def __init__(self):
        self.string = ""

    def custom_print(self, string):
        self.string = self.string + string + '\n'

    def get_string(self):
        return self.string

class Context:
    def id(self, x):
        return x

    def seq(self, x, y):
        return [x, y]

class EquivChecker:

    def __init__(self):
        self.clingo_output = []
        self.newground_output = []

        self.clingo_hashes = {}
        self.newground_hashes = {}

    def on_model(self, m, output, hashes):
        symbols = m.symbols(shown=True)
        output.append([])
        cur_pos = len(output) - 1
        for symbol in symbols:
            output[cur_pos].append(str(symbol))

        output[cur_pos].sort()

        hashes[(hash(tuple(output[cur_pos])))] = cur_pos

    def parse(self):
        parser = argparse.ArgumentParser(prog='Answerset Equivalence Checker', description='Checks equivalence of answersets produced by newground and clingo.')

        parser.add_argument('instance')
        parser.add_argument('encoding')
        args = parser.parse_args()

        instance_filename = args.instance
        encoding_filename = args.encoding

        if not os.path.isfile(instance_filename):
            print(f'Provided instance file \'{instance_filename}\' not found or is not a file')
            return
        if not os.path.isfile(encoding_filename):
            print(f'Provided encoding file \'{encoding_filename}\' not found or is not a file')
            return

        instance_file_contents = open(instance_filename, 'r').read()
        encoding_file_contents = open(encoding_filename, 'r').read()

        return (instance_file_contents, encoding_file_contents)



    def start(self, instance_file_contents, encoding_file_contents, verbose = True):

    
        ctl = clingo.Control()
        ctl.configuration.solve.models = 0
        ctl.add('base',[], instance_file_contents + encoding_file_contents)
        ctl.ground([('base',[])], context=Context())
        ctl.solve(on_model=lambda m: self.on_model(m, self.clingo_output, self.clingo_hashes))
        
        no_show = False
        ground_guess = False
        ground = False

        new_instance_file_contents = '#program facts.\n' + instance_file_contents
        new_encoding_file_contents = '#program rules.\n' + encoding_file_contents

        total_content = new_instance_file_contents + new_encoding_file_contents

        temp_file_name = 'temp_as_equiv_checker.py'
        open(temp_file_name, 'w').write(total_content)

        # no output from clingo itself
        #sys.argv.append("--outf=3")

        custom_printer = CustomOutputPrinter()

        block_print()

        ret_val =clingo.clingo_main(ClingoApp('newground', no_show, ground_guess, ground, custom_printer), [temp_file_name])

        enable_print()
        if ret_val == 0:
            ctl2 = clingo.Control()
            ctl2.configuration.solve.models = 0
            ctl2.add('base',[], custom_printer.get_string())
            ctl2.ground([('base',[])], context=Context())
            ctl2.solve(on_model=lambda m: self.on_model(m, self.newground_output, self.newground_hashes))

            works = True

            if len(self.clingo_output) != len(self.newground_output):
                works = False
            else:
                for clingo_key in self.clingo_hashes.keys():
                    if clingo_key not in self.newground_hashes:
                        works = False
                        if verbose:
                            print(f"Could not find corresponding stable model in newground for hash {clingo_key}")
                            print(f"This corresponds to the answer set: ")
                            print(self.clingo_output[self.clingo_hashes[clingo_key]])

            if not works:
                if verbose:
                    print("----------------------")
                    print("----------------------")
                    print("----------------------")
                    print("The answersets DIFFER!")
                    print(f"Clingo produced a total of {len(self.clingo_output)}")
                    print(f"Newground produced a total of {len(self.newground_output)}")

                return (False, len(self.clingo_output), len(self.newground_output))
            else: # works
                if verbose:
                    print("The answersets are the SAME!")

                return (True, len(self.clingo_output), len(self.newground_output))
        else: #ret_val != 0
            return (False, len(self.clingo_output), -1)


if __name__ == "__main__":
    checker = EquivChecker()
    (instance, encoding) = checker.parse()
    checker.start(instance, encoding)


