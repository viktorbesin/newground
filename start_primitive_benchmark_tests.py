import os
import sys
import argparse
import time
import subprocess

import tempfile

import clingo

from newground.newground import Newground
from newground.default_output_printer import DefaultOutputPrinter

class CustomOutputPrinter(DefaultOutputPrinter):

    def __init__(self):
        self.current_rule_hashes = {}
        self.string = ""

    def custom_print(self, string):
        string_hash = hash(string)

        if string_hash in self.current_rule_hashes:
            return
        else:
            self.current_rule_hashes[string_hash] = string_hash
            self.string = self.string + str(string) + '\n'

    def get_string(self):
        return self.string

class Context:
    def id(self, x):
        return x

    def seq(self, x, y):
        return [x, y]

class PrimitiveBenchmark:

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
        parser = argparse.ArgumentParser(prog='Primitive Benchmark', description='Benchmarks Newground vs. Clingo (total grounding + solving time).')

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


        temp_file = tempfile.NamedTemporaryFile()
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        clingo_start_time = time.time()   

        subprocess.run(["clingo",f"{temp_file.name}"])       

        clingo_end_time = time.time()   
        clingo_duration = clingo_end_time - clingo_start_time
        print(f"[INFO] - Clingo needed {clingo_duration} seconds!")

        """
        clingo_start_time = time.time()   
 
        ctl = clingo.Control()
        ctl.configuration.solve.models = 0
        ctl.add('base',[], instance_file_contents + encoding_file_contents)
        ctl.ground([('base',[])], context=Context())
        ctl.solve()
        #ctl.solve(on_model=lambda m: self.on_model(m, self.clingo_output, self.clingo_hashes))

        clingo_end_time = time.time()

        clingo_duration = clingo_end_time - clingo_start_time

        print(f"[INFO] - Clingo needed {clingo_duration} seconds!")
        """
        
        no_show = False
        ground_guess = False
        ground = False

        total_content = instance_file_contents + "\n#program rules.\n" + encoding_file_contents

        custom_printer = CustomOutputPrinter()
      
        newground_start_time = time.time()   

        newground = Newground(no_show = no_show, ground_guess = ground_guess, ground = ground, output_printer = custom_printer)
        newground.start(total_content)

        newground_end_time = time.time()   
        newground_duration_0 = newground_end_time - newground_start_time
        print(f"[INFO] - Newground duration 0:{newground_duration_0}")

        output_string = custom_printer.get_string()

        temp_file = tempfile.NamedTemporaryFile()
    
        with open(temp_file.name, "w") as f:
            f.write(output_string)

        newground_start_time = time.time()   

        subprocess.run(["clingo",f"{temp_file.name}"])       

        newground_end_time = time.time()   
        newground_duration_1 = newground_end_time - newground_start_time
        print(f"[INFO] - Newground duration 1:{newground_duration_1}")

        newground_total_duration = newground_duration_0 + newground_duration_1

        print(f"[INFO] - <<<<<<<<<<>>>>>>>>>>")
        print(f"[INFO] - Newground needed {newground_total_duration} seconds!")
        print(f"[INFO] - Clingo needed {clingo_duration} seconds!")


        """
        newground_start_time = time.time()   
        ctl2 = clingo.Control()
        ctl2.configuration.solve.models = 0

        ctl2.add('base',[], )
        ctl2.ground([('base',[])], context=Context())

        newground_end_time = time.time()
        print(f"[INFO] - Newground needed {newground_end_time - newground_start_time} seconds!")

        newground_start_time = time.time()   

        ctl2.solve()
        """
if __name__ == "__main__":
    checker = PrimitiveBenchmark()
    (instance, encoding) = checker.parse()
    checker.start(instance, encoding, verbose = True)



