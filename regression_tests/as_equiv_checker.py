import os
import sys
import argparse

import clingo

from newground.newground import Newground
from newground.default_output_printer import DefaultOutputPrinter

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
        self.string = self.string + str(string) + '\n'

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



    def start(self, instance_file_contents, encoding_file_contents, verbose = True, one_directional_equivalence = True):
        """ 
            one_directional_equivalence: If True, then only the direction clingo -> newground is checked, i.e. it must be the case, that for each answer set in the clingo result, there must be one in the newground result as well (but therefore it could be, that newground has more answersets)
        """

    
        ctl = clingo.Control()
        ctl.configuration.solve.models = 0
        ctl.add('base',[], instance_file_contents + encoding_file_contents)
        ctl.ground([('base',[])], context=Context())
        ctl.solve(on_model=lambda m: self.on_model(m, self.clingo_output, self.clingo_hashes))
        
        no_show = False
        ground_guess = False
        ground = False

        total_content = instance_file_contents + "\n#program rules.\n" + encoding_file_contents

        custom_printer = CustomOutputPrinter()
       

        newground = Newground(no_show = no_show, ground_guess = ground_guess, ground = ground, output_printer = custom_printer)
        newground.start(total_content)

        ctl2 = clingo.Control()
        ctl2.configuration.solve.models = 0
        ctl2.add('base',[], custom_printer.get_string())
        ctl2.ground([('base',[])], context=Context())
        ctl2.solve(on_model=lambda m: self.on_model(m, self.newground_output, self.newground_hashes))

        works = True

        if not one_directional_equivalence and len(self.clingo_output) != len(self.newground_output):
            works = False
        else:
            for clingo_key in self.clingo_hashes.keys():
                if clingo_key not in self.newground_hashes:
                    works = False
                    if verbose:
                        print(f"Could not find corresponding stable model in newground for hash {clingo_key}")
                        print(f"This corresponds to the answer set: ")
                        print(self.clingo_output[self.clingo_hashes[clingo_key]])

            for newground_key in self.newground_hashes.keys():
                if newground_key not in self.clingo_hashes:
                    works = False
                    if verbose:
                        print(f"Could not find corresponding stable model in clingo for hash {newground_key}")
                        print(f"This corresponds to the answer set: ")
                        print(self.newground_output[self.newground_hashes[newground_key]])



        if not works:
            if verbose:
                print("[INFO] ----------------------")
                print("[INFO] ----------------------")
                print("[INFO] ----------------------")
                print("[INFO] The answersets DIFFER!")
                print(f"[INFO] Clingo produced a total of {len(self.clingo_output)}")
                print(f"[INFO] Newground produced a total of {len(self.newground_output)}")

            return (False, len(self.clingo_output), len(self.newground_output))
        else: # works
            if verbose:
                print("[INFO] The answersets are the SAME!")

            return (True, len(self.clingo_output), len(self.newground_output))



