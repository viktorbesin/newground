#!/home/thinklex/programs/python3.11.3/bin/python3
import os
import sys
import io

import time

import subprocess

import tempfile
import argparse

import resource

def limit_virtual_memory():
    max_virtual_memory = 1024 * 1024 * 1024 * 32 # 32GB

    # TUPLE -> (soft limit, hard limit)
    resource.setrlimit(resource.RLIMIT_AS, (max_virtual_memory, max_virtual_memory))


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

    def parse(self, config, timeout = 1800, clingo_mockup = False, idlv_mockup = False, newground_idlv_mockup = False, newground_gringo_mockup = False, ground_and_solve = True, run_all_examples = False):
        parser = argparse.ArgumentParser(prog='Primitive Benchmark', description='Benchmarks Newground vs. Clingo (total grounding + solving time).')

        parser.add_argument('input_folder')
        parser.add_argument('output_file')
        args = parser.parse_args()

        input_path = args.input_folder
        output_filename = args.output_file

        instance_files = []

        for f in os.scandir(input_path):
            if f.is_file():
                if not "encoding" in str(f.name) and not "additional_instance" in str(f.name):
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
            write_string = "instance,gringo-duration,gringo-timeout-occured,idlv-duration,idlv-timeout-occured,newground-idlv-duration,newground-idlv-timeout-occured,newground-gringo-duration,newground-gringo-timeout-occured"
            output_file.write(write_string)

        with open(grounding_time_output_filename, "w") as output_file:
            write_string = "instance,gringo-duration,gringo-timeout-occured,idlv-duration,idlv-timeout-occured,newground-idlv-duration,newground-idlv-timeout-occured,newground-gringo-duration,newground-gringo-timeout-occured"
            output_file.write(write_string)

        with open(grounding_size_output_filename, "w") as output_file:
            write_string = "instance,gringo-size,gringo-timeout-occured,idlv-size,idlv-timeout-occured,newground-idlv-size,newground-idlv-timeout-occured,newground-gringo-size,newground-gringo-timeout-occured"
            output_file.write(write_string)

        # ------------------------ START BENCHMARK HERE -------------------------

        for instance_file in instance_files:
            print("")
            print(f">>>> Now solving: {instance_file}")
            print("")
            instance_path = os.path.join(input_path, instance_file)
            instance_file_contents = open(instance_path, 'r').read()

            instance_file_contents += additional_instance_file_contents

            print("GRINGO")
            if not clingo_mockup:
                gringo_clingo_timeout_occured, gringo_clingo_duration, gringo_duration, gringo_grounding_file_size  = Benchmark.clingo_benchmark(instance_file_contents, encoding_file_contents, config, timeout = timeout, ground_and_solve = ground_and_solve)
            else:
                gringo_clingo_timeout_occured = True
                gringo_clingo_duration = timeout
                gringo_duration = timeout
                gringo_grounding_file_size = 0

            print("IDLV")
            if not idlv_mockup:
                idlv_clingo_timeout_occured, idlv_clingo_duration, idlv_duration, idlv_grounding_file_size = Benchmark.idlv_benchmark(instance_file_contents, encoding_file_contents, config, timeout = timeout, ground_and_solve = ground_and_solve)
            else:
                idlv_clingo_timeout_occured = True
                idlv_clingo_duration = timeout
                idlv_duration = timeout
                idlv_grounding_file_size = 0

            print("NEWGROUND-IDLV")
            if not newground_idlv_mockup:
                newground_idlv_clingo_timeout_occured, newground_idlv_clingo_duration, newground_idlv_duration, newground_idlv_grounding_file_size = Benchmark.newground_benchmark(instance_file_contents, encoding_file_contents, config, timeout = timeout, grounder = "IDLV",ground_and_solve = ground_and_solve)
            else:
                newground_idlv_clingo_timeout_occured = True
                newground_idlv_clingo_duration = timeout
                newground_idlv_duration = timeout
                newground_idlv_grounding_file_size = 0

            print("NEWGROUND-GRINGO")
            if not newground_gringo_mockup:
                newground_gringo_clingo_timeout_occured, newground_gringo_clingo_duration, newground_gringo_duration, newground_gringo_grounding_file_size = Benchmark.newground_benchmark(instance_file_contents, encoding_file_contents, config, timeout = timeout, grounder = "GRINGO",ground_and_solve = ground_and_solve)
            else:
                newground_gringo_clingo_timeout_occured = True
                newground_gringo_clingo_duration = timeout
                newground_gringo_duration = timeout
                newground_gringo_grounding_file_size = 0
               

            # Print current console info:
            if gringo_clingo_timeout_occured:
                print(f"[INFO] - Clingo timed out ({gringo_clingo_duration})!")
            else:
                print(f"[INFO] - Clingo needed {gringo_clingo_duration} seconds!")

            if idlv_clingo_timeout_occured:
                print(f"[INFO] - IDLV timed out ({idlv_clingo_duration})!")
            else:
                print(f"[INFO] - IDLV needed {idlv_clingo_duration} seconds!")

            if newground_idlv_clingo_timeout_occured:
                print(f"[INFO] - Newground-IDLV timed out ({newground_idlv_clingo_duration})!")
            else:
                print(f"[INFO] - Newground-IDLV needed {newground_idlv_clingo_duration} seconds!")

            if newground_gringo_clingo_timeout_occured:
                print(f"[INFO] - Newground-GRINGO timed out ({newground_gringo_clingo_duration})!")
            else:
                print(f"[INFO] - Newground-GRINGO needed {newground_gringo_clingo_duration} seconds!")

            # Add info to .csv files
            with open(total_time_output_filename, "a") as output_file:
                output_file.write(f"\n{instance_file},{gringo_clingo_duration},{gringo_clingo_timeout_occured},{idlv_clingo_duration},{idlv_clingo_timeout_occured},{newground_idlv_clingo_duration},{newground_idlv_clingo_timeout_occured},{newground_gringo_clingo_duration},{newground_gringo_clingo_timeout_occured}")

            with open(grounding_time_output_filename, "a") as output_file:
                output_file.write(f"\n{instance_file},{gringo_duration},{gringo_clingo_timeout_occured},{idlv_duration},{idlv_clingo_timeout_occured},{newground_idlv_duration},{newground_idlv_clingo_timeout_occured},{newground_gringo_duration},{newground_gringo_clingo_timeout_occured}")

            with open(grounding_size_output_filename, "a") as output_file:
                output_file.write(f"\n{instance_file},{gringo_grounding_file_size},{gringo_clingo_timeout_occured},{idlv_grounding_file_size},{idlv_clingo_timeout_occured},{newground_idlv_grounding_file_size},{newground_idlv_clingo_timeout_occured},{newground_gringo_grounding_file_size},{newground_gringo_clingo_timeout_occured}")

            # Speed up benchmarks if specified to do so
            if not run_all_examples:
                if gringo_clingo_timeout_occured == True or gringo_clingo_duration >= timeout:
                    clingo_mockup = True

                if idlv_clingo_timeout_occured == True or idlv_clingo_duration >= timeout:
                    idlv_mockup = True

                if newground_idlv_clingo_timeout_occured == True or newground_idlv_clingo_duration >= timeout:
                    newground_idlv_mockup = True

                if newground_gringo_clingo_timeout_occured == True or newground_gringo_clingo_duration >= timeout:
                    newground_gringo_mockup = True



    @classmethod
    def idlv_benchmark(cls, instance_file_contents, encoding_file_contents, config, timeout = 1800, ground_and_solve = True):

        idlv_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile(mode="w+")
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        idlv_start_time = time.time()   

        temp_grounding_file = tempfile.NamedTemporaryFile(mode="w+")
        temp_grounding_file_fd = open(temp_grounding_file.name, "w")

        try:
            p = subprocess.Popen([config["idlv_command"], f"{temp_file.name}"], stdout=temp_grounding_file_fd, preexec_fn=limit_virtual_memory)       
            p.communicate( timeout = timeout)[0]

            idlv_duration = time.time() - idlv_start_time

            if p.returncode != 0:
                idlv_out_of_time = True
                idlv_duration = timeout



        except Exception as ex:
            print(ex)
            idlv_out_of_time = True
            idlv_duration = timeout



        temp_grounding_file_fd.flush()
        temp_grounding_file_fd.close()
        grounding_file_size_bytes = os.path.getsize(temp_grounding_file.name)
        grounding_file_size_kb = grounding_file_size_bytes / 1024

        temp_grounding_file_fd = open(temp_grounding_file.name, "r")

        clingo_start_time = time.time()

        if idlv_out_of_time == False and idlv_duration < timeout and ground_and_solve:

            try:
                p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=temp_grounding_file_fd, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory) 

                output = p.communicate(timeout = (timeout - idlv_duration))[0]

                if p.returncode != 10 and p.returncode != 20:
                    idlv_out_of_time = True
                    idlv_duration = timeout
                #print(output.decode().strip())

            except Exception as ex:
                print(ex)
                idlv_out_of_time = True

        clingo_end_time = time.time()   
        idlv_clingo_duration = clingo_end_time - clingo_start_time + idlv_duration

        return (idlv_out_of_time, idlv_clingo_duration, idlv_duration, grounding_file_size_kb)
           
    @classmethod
    def clingo_benchmark(cls, instance_file_contents, encoding_file_contents, config, timeout = 1800, ground_and_solve = True):

        clingo_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile("w+")
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        gringo_start_time = time.time()   

        temp_grounding_file = tempfile.NamedTemporaryFile(mode="w+")
        temp_grounding_file_fd = open(temp_grounding_file.name, "w")

        try:
            p = subprocess.Popen([config["gringo_command"], f"{temp_file.name}"], stdout=temp_grounding_file_fd, preexec_fn=limit_virtual_memory)       
            p.communicate( timeout = timeout)[0]

            gringo_duration = time.time() - gringo_start_time

            if p.returncode != 0:
                clingo_out_of_time = True
                gringo_duration = timeout

        except Exception as ex:
            print(ex)
            clingo_out_of_time = True
            gringo_duration = timeout



        temp_grounding_file_fd.flush()
        temp_grounding_file_fd.close()
        grounding_file_size_bytes = os.path.getsize(temp_grounding_file.name)
        grounding_file_size_kb = grounding_file_size_bytes / 1024

        temp_grounding_file_fd = open(temp_grounding_file.name, "r")

        clingo_start_time = time.time()

        if clingo_out_of_time == False and gringo_duration < timeout and ground_and_solve:
            try:
                p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=temp_grounding_file_fd, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
                output = p.communicate(timeout = (timeout - gringo_duration))[0]

                if p.returncode != 10 and p.returncode != 20:
                    clingo_out_of_time = True
                    gringo_duration = timeout

                #print(output.decode().strip())
            except Exception as ex:
                print(ex)
                clingo_out_of_time = True

        clingo_end_time = time.time()   
        gringo_clingo_duration = clingo_end_time - clingo_start_time + gringo_duration

        return (clingo_out_of_time, gringo_clingo_duration, gringo_duration, grounding_file_size_kb)

    @classmethod
    def newground_benchmark(cls, instance_file_contents, encoding_file_contents, config, timeout = 1800, grounder = "IDLV", ground_and_solve = True):

        temp_file = tempfile.NamedTemporaryFile("w+")

        total_contents = f"{instance_file_contents}\n#program rules.\n{encoding_file_contents}"

        with open(temp_file.name, "w") as f:
            f.write(total_contents)

        temp_file_2 = tempfile.NamedTemporaryFile("w+")
        temp_file_2_fd = open(temp_file_2.name, "w")

        newground_out_of_time = False

        newground_start_time = time.time()   

        try: 
            p = subprocess.Popen([config["python_command"], "start_newground.py", config["rewriting_strategy"],  f"{temp_file.name}"], stdout=temp_file_2_fd, preexec_fn=limit_virtual_memory)       

            p.communicate(timeout = timeout)

            newground_duration = time.time() - newground_start_time

            if p.returncode != 0:
                newground_out_of_time = True
                newground_duration = timeout



        except Exception as ex:
            print(ex)
            newground_out_of_time = True
            newground_duration = timeout

        temp_file_2_fd.close()
        temp_file_2_fd = open(temp_file_2.name, "r")

        temp_grounding_file = tempfile.NamedTemporaryFile(mode="w+")
        temp_grounding_file_fd = open(temp_grounding_file.name, "w")


        gringo_start = time.time()

        if newground_out_of_time == False and newground_duration < timeout:

            try:
                if grounder == "IDLV":
                    p = subprocess.Popen([config["idlv_command"], f"{temp_file_2.name}"], stdout=temp_grounding_file_fd, preexec_fn=limit_virtual_memory)       
                    p.communicate( timeout = (timeout - newground_duration))

                elif grounder == "GRINGO":

                    p = subprocess.Popen([config["gringo_command"]], stdout=temp_grounding_file_fd, stdin=temp_file_2_fd, preexec_fn=limit_virtual_memory)       
                    p.communicate(timeout = (timeout - newground_duration))

                newground_duration += (time.time() - gringo_start)

                if p.returncode != 0:
                    newground_out_of_time = True
                    newground_duration = timeout

            except Exception as ex:
                print(ex)
                newground_out_of_time = True
                newground_duration = timeout


        temp_grounding_file_fd.flush()
        temp_grounding_file_fd.close()
        grounding_file_size_bytes = os.path.getsize(temp_grounding_file.name)
        grounding_file_size_kb = grounding_file_size_bytes / 1024

        temp_grounding_file_fd = open(temp_grounding_file.name, "r")

        clingo_start_time = time.time()

        if newground_out_of_time == False and newground_duration < timeout and ground_and_solve:
            try:
                p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=temp_grounding_file_fd, stdout = subprocess.PIPE, preexec_fn=limit_virtual_memory) 

                output = p.communicate(timeout = (timeout - newground_duration))[0]


                if p.returncode != 10 and p.returncode != 20: # Clingo return code for everything fine
                    newground_out_of_time = True
                    newground_duration = timeout

                #print(output.decode().strip())

            except Exception as ex:
                print(ex)
                newground_out_of_time = True

        clingo_end_time = time.time()   
        newground_clingo_duration = clingo_end_time - clingo_start_time + newground_duration

        return (newground_out_of_time, newground_clingo_duration, newground_duration, grounding_file_size_kb)

if __name__ == "__main__":

    config = {}
    config["clingo_command"] = "./clingo"
    config["gringo_command"] = "./gringo"
    config["idlv_command"] = "./idlv.bin"
    config["python_command"] = "./python3"

    # Strategies ->  {replace,rewrite,rewrite-no-body}
    config["rewriting_strategy"] = "--aggregate-strategy=rewrite-no-body"
    #config["rewriting_strategy"] = "--aggregate-strategy=rewrite"
    #config["rewriting_strategy"] = "--aggregate-strategy=replace"

    checker = Benchmark()

    timeout = 1800

    clingo_mockup = False
    idlv_mockup = False
    newground_idlv_mockup = False
    newground_gringo_mockup = False

    ground_and_solve = True
    run_all_examples = True


    checker.parse(config, timeout = timeout, clingo_mockup = clingo_mockup, idlv_mockup = idlv_mockup, newground_idlv_mockup = newground_idlv_mockup, newground_gringo_mockup = newground_gringo_mockup, ground_and_solve = ground_and_solve)





