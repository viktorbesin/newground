#!/home/thinklex/programs/python3.11.3/bin/python3
import os
import sys
import io

import time
import re

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

        self.clingo_command = "./clingo"
        self.gringo_command = "./gringo"
        self.idlv_command = "./idlv"
        self.python_command = "./python3"

        # Strategies ->  {replace,rewrite,rewrite-no-body}
        #self.rewriting_strategy = "--aggregate-strategy=rewrite-no-body"
        #self.rewriting_strategy = "--aggregate-strategy=rewrite"
        self.rewriting_strategy = "--aggregate-strategy=replace"


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

        # If set to false -> Benchmark -> otherwise use mokcup (i.e. skip)
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
                gringo_clingo_timeout_occured = True
                gringo_clingo_duration = 1800
                gringo_duration = 1800
                gringo_grounding_file_size = 0

            print("IDLV")
            if not idlv_mockup:
                idlv_clingo_timeout_occured, idlv_clingo_duration, idlv_duration, idlv_grounding_file_size = self.idlv_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                idlv_clingo_timeout_occured = True
                idlv_clingo_duration = 1800
                idlv_duration = 1800
                idlv_grounding_file_size = 0

            print("NEWGROUND")
            if not newground_mockup:
                newground_clingo_timeout_occured, newground_clingo_duration, newground_duration, newground_grounding_file_size = self.newground_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                newground_clingo_timeout_occured = True
                newground_clingo_duration = 1800
                newground_duration = 1800
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

            if gringo_clingo_timeout_occured == True or gringo_clingo_duration >= 1800:
                clingo_mockup = True

            if idlv_clingo_timeout_occured == True or idlv_clingo_duration >= 1800:
                idlv_mockup = True

            if newground_clingo_timeout_occured == True or newground_clingo_duration >= 1800:
                newground_mockup = True

    def dlv_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):
        """
            Deprecated
        """

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
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        idlv_start_time = time.time()   

        output = None

        if timeout == None:
            p = subprocess.Popen(["./idlv.bin", f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
            output = p.communicate()[0]
            output = output.decode().strip().encode()

            if p.returncode != 0:
                idlv_out_of_time = True
                idlv_duration = 1800



        else:
            try:
                p = subprocess.Popen(["./idlv.bin", f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
                output = p.communicate( timeout = timeout)[0]
                output = output.decode().strip().encode()

                #print(output)
                idlv_duration = time.time() - idlv_start_time

                if p.returncode != 0:
                    idlv_out_of_time = True
                    idlv_duration = 1800



            except Exception as ex:
                print(ex)
                idlv_out_of_time = True
                idlv_duration = 1800


        clingo_start_time = time.time()


        if idlv_out_of_time == False and output != None and idlv_duration < timeout:

            grounding_file_size_bytes = len(output)
            grounding_file_size_kb = grounding_file_size_bytes / 1024



            if timeout == None:
                p = subprocess.Popen([self.clingo_command,"--mode=clasp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

                output = p.communicate(input = output)

                if p.returncode != 0:
                    idlv_out_of_time = True
                    idlv_duration = 1800


                #print(output.decode().strip())

            else:
                try:
                    p = subprocess.Popen([self.clingo_command,"--mode=clasp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory) 
                    output = p.communicate(input = output, timeout = (timeout - idlv_duration))[0]

                    if p.returncode != 10 and p.returncode != 20:
                        idlv_out_of_time = True
                        idlv_duration = 1800



                    #print(output.decode().strip())

                except Exception as ex:
                    print(ex)
                    idlv_out_of_time = True
        else:
            grounding_file_size_kb = 0

        clingo_end_time = time.time()   
        idlv_clingo_duration = clingo_end_time - clingo_start_time + idlv_duration

        return (idlv_out_of_time, idlv_clingo_duration, idlv_duration, grounding_file_size_kb)
            
    def clingo_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        clingo_out_of_time = False
        temp_file = tempfile.NamedTemporaryFile("w+")
    
        with open(temp_file.name, "w") as f:
            f.write(instance_file_contents + encoding_file_contents)

        gringo_start_time = time.time()   

        output = None
        if timeout == None:
            p = subprocess.Popen([self.gringo_command, f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
            output = p.communicate()[0]
            output = output.decode().strip().encode()

            gringo_duration = time.time() - gringo_start_time

            if p.returncode != 0:
                clingo_out_of_time = True
                gringo_duration = 1800



        else:
            try:
                p = subprocess.Popen([self.gringo_command, f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
                output = p.communicate( timeout = timeout)[0]
                output = output.decode().strip().encode()

                gringo_duration = time.time() - gringo_start_time

                if p.returncode != 0:
                    clingo_out_of_time = True
                    gringo_duration = 1800




            except Exception as ex:
                print(ex)
                clingo_out_of_time = True
                gringo_duration = 1800


        clingo_start_time = time.time()

        if clingo_out_of_time == False and output != None and gringo_duration < timeout:

            grounding_file_size = len(output)
            grounding_file_size_kb = grounding_file_size / 1024



            if timeout == None:
                p = subprocess.Popen([self.clingo_command,"--mode=clasp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

                output = p.communicate(input = output)[0]
                if p.returncode != 0:
                    clingo_out_of_time = True
                    gringo_duration = 1800



                
            else:
                try:
                    p = subprocess.Popen([self.clingo_command,"--mode=clasp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
                    output = p.communicate(input = output, timeout = (timeout - gringo_duration))[0]

                    if p.returncode != 10 and p.returncode != 20:
                        clingo_out_of_time = True
                        gringo_duration = 1800



                    #print(output.decode().strip())
                except Exception as ex:
                    print(ex)
                    clingo_out_of_time = True
        else:
            grounding_file_size_kb = 0

        clingo_end_time = time.time()   
        gringo_clingo_duration = clingo_end_time - clingo_start_time + gringo_duration

        return (clingo_out_of_time, gringo_clingo_duration, gringo_duration, grounding_file_size_kb)

    def newground_benchmark(self, instance_file_contents, encoding_file_contents, timeout = None):

        temp_file = tempfile.NamedTemporaryFile("w+")

        total_contents = f"{instance_file_contents}\n#program rules.\n{encoding_file_contents}"

        with open(temp_file.name, "w") as f:
            f.write(total_contents)

        newground_out_of_time = False

        newground_start_time = time.time()   

        output = None
        if timeout == None:
            p = subprocess.Popen([self.python_command, "start_newground.py", self.rewriting_strategy, f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

            output = p.communicate()[0]
            output = output.decode().strip()

            newground_duration = time.time() - newground_start_time
 
            if p.returncode != 0:
                newground_out_of_time = True
                newground_duration = 1800

          
        else:
            try:
                p = subprocess.Popen([self.python_command, "start_newground.py", self.rewriting_strategy,  f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

                output = p.communicate(timeout = timeout)[0]
                output = output.decode().strip()

                newground_duration = time.time() - newground_start_time

                print(p.returncode)
                print(p.returncode == 0)
                print(int(p.returncode) == 0)


                if p.returncode != 0:
                    newground_out_of_time = True
                    newground_duration = 1800



            except Exception as ex:
                print(ex)
                newground_out_of_time = True
                newground_duration = 1800


        gringo_start = time.time()

        if newground_out_of_time == False and output != None and newground_duration < timeout:

            if timeout == None:
                subprocess.Popen([self.gringo_command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

                output = p.communicate(input = output.encode())[0]
                output = output.decode().strip().encode()
               
                newground_duration += (time.time() - gringo_start)

                if p.returncode != 0:
                    newground_out_of_time = True
                    newground_duration = 1800


            else:
                try:
                    p = subprocess.Popen([self.gringo_command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

                    output = p.communicate(input = output.encode(), timeout = (timeout - newground_duration))[0]
                    output.decode().strip().encode()


                    newground_duration += (time.time() - gringo_start)

                    print(p.returncode)
                    print(p.returncode == 0)
                    print(int(p.returncode) == 0)


                    if p.returncode != 0:
                        newground_out_of_time = True
                        newground_duration = 1800



                except Exception as ex:
                    print(ex)
                    newground_out_of_time = True
                    newground_duration = 1800


        clingo_start_time = time.time()

        if newground_out_of_time == False and output != None and newground_duration < timeout:

            grounding_file_size_bytes = len(output)
            grounding_file_size_kb = grounding_file_size_bytes / 1024

            if timeout == None:
                p = subprocess.Popen([self.clingo_command,"--mode=clasp"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, preexec_fn=limit_virtual_memory)

                output = p.communicate(input = output)

                if p.returncode != 0:
                    newground_out_of_time = True
                    newground_duration = 1800


            else:
                try:
                    p = subprocess.Popen([self.clingo_command,"--mode=clasp"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, preexec_fn=limit_virtual_memory) 

                    output = p.communicate(input = output, timeout = (timeout - newground_duration))[0]

                    print(p.returncode)
                    print(p.returncode == 0)
                    print(int(p.returncode) == 0)


                    if p.returncode != 10 and p.returncode != 20: # Clingo return code for everything fine
                        newground_out_of_time = True
                        newground_duration = 1800


                    #print(output.decode().strip())

                except Exception as ex:
                    print(ex)
                    newground_out_of_time = True
        else:
            grounding_file_size_kb = 0

        clingo_end_time = time.time()   
        newground_clingo_duration = clingo_end_time - clingo_start_time + newground_duration

        return (newground_out_of_time, newground_clingo_duration, newground_duration, grounding_file_size_kb)

if __name__ == "__main__":
    checker = Benchmark()

    timeout = 1800
    checker.parse(timeout = timeout)



