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
from newground.aggregate_transformer import AggregateMode

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

    def __init__(self, instance_file_contents, encoding_file_contents, timeout = None, aggregate_strategy = AggregateMode.REPLACE):
        self.instance_file_contents = instance_file_contents
        self.encoding_file_contents = encoding_file_contents
        self.timeout = timeout
        self.aggregate_strategy = aggregate_strategy

    def newground_helper_start(self):

        newground_start_time = time.time()   

        custom_printer = CustomOutputPrinter() 
        total_content = f"{self.instance_file_contents}\n#program rules.\n{self.encoding_file_contents}"
        
        newground = Newground(no_show = False, ground_guess = False, ground = False, output_printer = custom_printer, aggregate_strategy = self.aggregate_strategy)
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

        clingo_mockup = False
        newground_mockup = False
        idlv_mockup = False

        parser.add_argument('input_folder')
        parser.add_argument('output_file')
        args = parser.parse_args()

        input_path = args.input_folder
        output_filename = args.output_file

        instance_pattern = re.compile("^instance_[0-9][0-9][0-9]\.lp$")

        instance_files = []

        for f in os.scandir(input_path):
            if f.is_file():
                if instance_pattern.match(str(f.name)):
                    instance_files.append(str(f.name))

        instance_files.sort()


        encoding_path = os.path.join(input_path, "encoding.lp")
        encoding_file_contents = open(encoding_path, 'r').read()

        additional_instance_path = os.path.join(input_path, "additional_instance.lp")
        additional_instance_file_contents = open(additional_instance_path, 'r').read()

        total_time_output_filename = f"{output_filename}_total_time.csv"
        grounding_time_output_filename = f"{output_filename}_grounding_time.csv"
        grounding_size_output_filename = f"{output_filename}_grounding_size.csv"

        with open(total_time_output_filename, "w") as output_file:
            write_string = "instance,gringo-duration,gringo-timeout-occured,idlv-duration,idlv-timeout-occured,newground-duration,newground-timeout-occured\n"
            output_file.write(write_string)

        with open(grounding_time_output_filename, "w") as output_file:
            write_string = "instance,gringo-duration,gringo-timeout-occured,idlv-duration,idlv-timeout-occured,newground-duration,newground-timeout-occured\n"
            output_file.write(write_string)

        with open(grounding_size_output_filename, "w") as output_file:
            write_string = "instance,gringo-size,gringo-timeout-occured,idlv-size,idlv-timeout-occured,newground-size,newground-timeout-occured\n"
            output_file.write(write_string)



        for instance_file in instance_files:
            print("")
            print(f">>>> Now solving: {instance_file}")
            print("")
            instance_path = os.path.join(input_path, instance_file)
            instance_file_contents = open(instance_path, 'r').read()

            instance_file_contents += additional_instance_file_contents

            print("GRINGO")
            if not clingo_mockup:
                gringo_clingo_timeout_occured, gringo_clingo_duration, gringo_duration, gringo_grounding_file_size  = self.clingo_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                gringo_clingo_timeout_occured = False
                gringo_clingo_duration = 0
                gringo_duration = 0
                gringo_grounding_file_size = 0

            print("IDLV")
            if not idlv_mockup:
                idlv_clingo_timeout_occured, idlv_clingo_duration, idlv_duration, idlv_grounding_file_size = self.idlv_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                idlv_clingo_timeout_occured = False
                idlv_clingo_duration = 0
                idlv_duration = 0
                idlv_grounding_file_size = 0

            print("NEWGROUND")
            if not newground_mockup:
                newground_clingo_timeout_occured, newground_clingo_duration, newground_duration, newground_grounding_file_size = self.newground_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                newground_clingo_timeout_occured = False
                newground_clingo_duration = 0
                newground_duration = 0
                newground_grounding_file_size = 0

        
            """
            DLV
            """
            #dlv_timeout_occured, dlv_duration = self.dlv_benchmark(instance_file_contents, encoding_file_contents, timeout)
            #dlv_timeout_occured = False
            #dlv_duration = 0

            if gringo_clingo_timeout_occured:
                print(f"[INFO] - Clingo timed out ({gringo_clingo_duration})!")
            else:
                print(f"[INFO] - Clingo needed {gringo_clingo_duration} seconds!")

            if idlv_clingo_timeout_occured:
                print(f"[INFO] - IDlv timed out ({idlv_clingo_duration})!")
            else:
                print(f"[INFO] - IDlv needed {idlv_clingo_duration} seconds!")

            if newground_clingo_timeout_occured:
                print(f"[INFO] - Newground timed out ({newground_clingo_duration})!")
            else:
                print(f"[INFO] - Newground needed {newground_clingo_duration} seconds!")



            with open(total_time_output_filename, "a") as output_file:
                output_file.write(f"\n{instance_file},{gringo_clingo_duration},{gringo_clingo_timeout_occured},{idlv_clingo_duration},{idlv_clingo_timeout_occured},{newground_clingo_duration},{newground_clingo_timeout_occured}")


            with open(grounding_time_output_filename, "a") as output_file:
                output_file.write(f"\n{instance_file},{gringo_duration},{gringo_clingo_timeout_occured},{idlv_duration},{idlv_clingo_timeout_occured},{newground_duration},{newground_clingo_timeout_occured}")

            with open(grounding_size_output_filename, "a") as output_file:
                output_file.write(f"\n{instance_file},{gringo_grounding_file_size},{gringo_clingo_timeout_occured},{idlv_grounding_file_size},{idlv_clingo_timeout_occured},{newground_grounding_file_size},{newground_clingo_timeout_occured}")



    def dlv_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        clingo_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile()
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        clingo_start_time = time.time()   


        if timeout == None:
            subprocess.run(["./dlv.bin",f"{temp_file.name}","-n=1"])       
        else:
            try:
                subprocess.run(["./dlv.bin",f"{temp_file.name}","-n=1"], timeout = timeout)       
            except Exception as ex:
                clingo_out_of_time = True

        clingo_end_time = time.time()   
        clingo_duration = clingo_end_time - clingo_start_time

        return (clingo_out_of_time, clingo_duration)

    def idlv_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        idlv_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile(mode="w+")
        temp_file_2 = tempfile.NamedTemporaryFile(mode="w+")
    
        #with open(temp_file.name, "w") as f:
        #    f.write(instance_file_contents + encoding_file_contents)
        temp_file.write(instance_file_contents + encoding_file_contents)
        temp_file.flush()

        temp_file.seek(0)

        idlv_start_time = time.time()   

        output = None

        temp_file_2.flush()

        if timeout == None:
            output = subprocess.run(["./idlv.bin", f"{temp_file.name}"], stdout=temp_file_2)       
            
        else:
            try:
                output = subprocess.run(["./idlv.bin", f"{temp_file.name}"], timeout = timeout, stdout=temp_file_2)       
                #output = subprocess.run(["./idlv.bin", "--output=1", f"{temp_file.name}"], timeout = timeout, stdout=temp_file_2)       
            except Exception as ex:
                idlv_out_of_time = True

        idlv_duration = time.time() - idlv_start_time

        temp_file_2.flush()
        temp_file_2.seek(0)

        grounding_file_stats = os.stat(temp_file_2.name) 
        grounding_file_size_kb = grounding_file_stats.st_size / 1024

        clingo_start_time = time.time()

        if output != None and idlv_duration < timeout:

            if timeout == None:
                subprocess.run(["clingo","--mode=clasp",f"{temp_file_2.name}"])       
            else:
                try:
                    subprocess.run(["clingo","--mode=clasp",f"{temp_file_2.name}"], timeout = (timeout - idlv_duration)) 
                except Exception as ex:
                    idlv_out_of_time = True

        clingo_end_time = time.time()   
        idlv_clingo_duration = clingo_end_time - clingo_start_time + idlv_duration

        return (idlv_out_of_time, idlv_clingo_duration, idlv_duration, grounding_file_size_kb)
            
    def clingo_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        clingo_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile("w+")
        temp_file_2 = tempfile.NamedTemporaryFile("w+")
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        gringo_start_time = time.time()   

        output = None
        if timeout == None:
            output = subprocess.run(["gringo", f"{temp_file.name}"], stdout=temp_file_2)       
            
        else:
            try:
                output = subprocess.run(["gringo", f"{temp_file.name}"], timeout = timeout, stdout=temp_file_2)       
            except Exception as ex:
                clingo_out_of_time = True

        gringo_duration = time.time() - gringo_start_time

        temp_file_2.flush()
        temp_file_2.seek(0)

        grounding_file_stats = os.stat(temp_file_2.name) 
        grounding_file_size_kb = grounding_file_stats.st_size / 1024

        clingo_start_time = time.time()

        if output != None and gringo_duration < timeout:

            if timeout == None:
                subprocess.run(["clingo","--mode=clasp",f"{temp_file_2.name}"])       
            else:
                try:
                    subprocess.run(["clingo","--mode=clasp",f"{temp_file_2.name}"], timeout = (timeout - gringo_duration))       
                except Exception as ex:
                    clingo_out_of_time = True

        clingo_end_time = time.time()   
        gringo_clingo_duration = clingo_end_time - clingo_start_time + gringo_duration

        return (clingo_out_of_time, gringo_clingo_duration, gringo_duration, grounding_file_size_kb)

    def newground_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        temp_file = tempfile.NamedTemporaryFile("w+")
        temp_file_2 = tempfile.NamedTemporaryFile("w+")
        temp_file_3 = tempfile.NamedTemporaryFile("w+")

        total_contents = f"{instance_file_contents}\n#program rules.\n{encoding_file_contents}"
 
        with open(temp_file.name, "w") as f:
            f.write(total_contents)

        newground_out_of_time = False

        newground_start_time = time.time()   

        output = None
        if timeout == None:
            output = subprocess.run(["python", "start_newground.py", f"{temp_file.name}"], stdout=temp_file_2)       
            
        else:
            try:
                output = subprocess.run(["python", "start_newground.py", f"{temp_file.name}"], timeout = timeout, stdout=temp_file_2)       
            except Exception as ex:
                newground_out_of_time = True

        newground_duration = time.time() - newground_start_time

        temp_file_2.flush()
        temp_file_2.seek(0)

        gringo_start = time.time()

        if output != None and newground_duration < timeout:

            if timeout == None:
                subprocess.run(["gringo",f"{temp_file_2.name}"], stdout=temp_file_3)       
            else:
                try:
                    subprocess.run(["gringo",f"{temp_file_2.name}"], timeout = (timeout - newground_duration), stdout=temp_file_3)       
                except Exception as ex:
                    newground_out_of_time = True

        newground_duration += (time.time() - gringo_start)

        temp_file_3.flush()
        temp_file_3.seek(0)

        grounding_file_stats = os.stat(temp_file_3.name) 
        grounding_file_size_kb = grounding_file_stats.st_size / 1024

        clingo_start_time = time.time()

        if output != None and newground_duration < timeout:

            if timeout == None:
                subprocess.run(["clingo","--mode=clasp",f"{temp_file_3.name}"])       
            else:
                try:
                    subprocess.run(["clingo","--mode=clasp",f"{temp_file_3.name}"], timeout = (timeout - newground_duration))       
                except Exception as ex:
                    newground_out_of_time = True

        clingo_end_time = time.time()   
        newground_clingo_duration = clingo_end_time - clingo_start_time + newground_duration

        return (newground_out_of_time, newground_clingo_duration, newground_duration, grounding_file_size_kb)

if __name__ == "__main__":
    checker = Benchmark()

    timeout = 1800
    checker.parse(timeout)



