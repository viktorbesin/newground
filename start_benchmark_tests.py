import os
import sys
import argparse
import time
import subprocess

import re
import multiprocessing

import tempfile

import clingo

from newground.newground import Newground
from newground.default_output_printer import DefaultOutputPrinter

def handler(signum, frame):
    print("Benchmark timeout")
    raise Exception("end of time")

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

class NewgroundHelper:

    def __init__(self, instance_file_contents, encoding_file_contents, timeout = None):
        self.instance_file_contents = instance_file_contents
        self.encoding_file_contents = encoding_file_contents
        self.timeout = timeout

    def newground_helper_start(self):

        newground_start_time = time.time()   

        custom_printer = CustomOutputPrinter() 
        total_content = f"{self.instance_file_contents}\n#program rules.\n{self.encoding_file_contents}"
        
        newground = Newground(no_show = False, ground_guess = False, ground = False, output_printer = custom_printer)
        newground.start(total_content)

        newground_end_time = time.time()   
        newground_duration_0 = newground_end_time - newground_start_time

        output_string = custom_printer.get_string()

        temp_file = tempfile.NamedTemporaryFile()
    
        with open(temp_file.name, "w") as f:
            f.write(output_string)

        newground_start_time = time.time()   

        subprocess.run(["clingo",f"{temp_file.name}"])       

        newground_end_time = time.time()   
        newground_duration_1 = newground_end_time - newground_start_time

        newground_total_duration = newground_duration_0 + newground_duration_1



class Context:
    def id(self, x):
        return x

    def seq(self, x, y):
        return [x, y]

class Benchmark:

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

    def parse(self, timeout = None):
        parser = argparse.ArgumentParser(prog='Primitive Benchmark', description='Benchmarks Newground vs. Clingo (total grounding + solving time).')

        parser.add_argument('input_folder')
        parser.add_argument('output_file')
        args = parser.parse_args()

        input_path = args.input_folder
        output_filename = args.output_file

        instance_pattern = re.compile("^instance_[0-9][0-9]\.lp$")

        instance_files = []

        for f in os.scandir(input_path):
            if f.is_file():
                if instance_pattern.match(str(f.name)):
                    instance_files.append(str(f.name))

        instance_files.sort()


        encoding_path = os.path.join(input_path, "encoding.lp")
        encoding_file_contents = open(encoding_path, 'r').read()

        output_data = []

        for instance_file in instance_files:
            print("")
            print(f">>>> Now solving: {instance_file}")
            print("")
            instance_path = os.path.join(input_path, instance_file)
            instance_file_contents = open(instance_path, 'r').read()

            #clingo_timeout_occured, clingo_duration = self.clingo_benchmark(instance_file_contents, encoding_file_contents, timeout)
            dlv_timeout_occured, dlv_duration = self.dlv_benchmark(instance_file_contents, encoding_file_contents, timeout)
            #newground_timeout_occured, newground_duration = self.newground_benchmark(instance_file_contents, encoding_file_contents, timeout)

            clingo_timeout_occured = False
            clingo_duration = 0

            newground_timeout_occured = False
            newground_duration = 0




            if clingo_timeout_occured:
                print(f"[INFO] - Clingo timed out ({clingo_duration})!")
            else:
                print(f"[INFO] - Clingo needed {clingo_duration} seconds!")

            if dlv_timeout_occured:
                print(f"[INFO] - Dlv timed out ({dlv_duration})!")
            else:
                print(f"[INFO] - Dlv needed {dlv_duration} seconds!")



            if newground_timeout_occured:
                print(f"[INFO] - Newground timed out ({newground_duration})!")
            else:
                print(f"[INFO] - Newground needed {newground_duration} seconds!")

            output_data.append(f"{instance_file},{clingo_duration},{clingo_timeout_occured},{newground_duration},{newground_timeout_occured}")

        with open(output_filename, "w") as output_file:
            
            write_string = "instance,clingo-duration,clingo-timeout-occured,newground-duration,newground-timeout-occured\n"
            write_string += '\n'.join(output_data)

            output_file.write(write_string)

    def dlv_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        clingo_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile()
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        clingo_start_time = time.time()   


        if timeout == None:
            subprocess.run(["./dlv.bin",f"{temp_file.name}"])       
        else:
            try:
                subprocess.run(["./dlv.bin",f"{temp_file.name}"], timeout = timeout)       
            except Exception as ex:
                clingo_out_of_time = True

        clingo_end_time = time.time()   
        clingo_duration = clingo_end_time - clingo_start_time

        return (clingo_out_of_time, clingo_duration)
            
    def clingo_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        clingo_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile()
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        clingo_start_time = time.time()   

        if timeout == None:
            subprocess.run(["clingo",f"{temp_file.name}"])       
        else:
            try:
                subprocess.run(["clingo",f"{temp_file.name}"], timeout = timeout)       
            except Exception as ex:
                clingo_out_of_time = True

        clingo_end_time = time.time()   
        clingo_duration = clingo_end_time - clingo_start_time

        return (clingo_out_of_time, clingo_duration)

    def newground_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        newground_helper = NewgroundHelper(instance_file_contents, encoding_file_contents)
        newground_out_of_time = False

        start_time = time.time()

        if timeout == None:
            newground_helper.newground_helper_start()
        else:
            p = multiprocessing.Process(target=newground_helper.newground_helper_start)
            p.start()
            p.join(timeout)
            if p.is_alive():
                newground_out_of_time = True
                print("Running ... let's kill it")
                p.terminate()
                p.join()

        end_time = time.time()

        return (newground_out_of_time, end_time - start_time)


if __name__ == "__main__":
    checker = Benchmark()

    timeout = 1800
    checker.parse(timeout)



