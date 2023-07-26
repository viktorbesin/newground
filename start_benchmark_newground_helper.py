import sys
import base64
import json
import pickle

import os
import io

import time

import subprocess
from subprocess import TimeoutExpired

import tempfile
import argparse

import resource

from start_benchmark_utils import StartBenchmarkUtils

def limit_virtual_memory():
    max_virtual_memory = 1024 * 1024 * 1024 * 32 # 32GB

    # TUPLE -> (soft limit, hard limit)
    resource.setrlimit(resource.RLIMIT_AS, (max_virtual_memory, max_virtual_memory))

config = StartBenchmarkUtils.decode_argument(sys.argv[1])
timeout = StartBenchmarkUtils.decode_argument(sys.argv[2])
ground_and_solve = StartBenchmarkUtils.decode_argument(sys.argv[3])
grounder = StartBenchmarkUtils.decode_argument(sys.argv[4])

input_code = sys.stdin.read()

temp_file = tempfile.NamedTemporaryFile("w+")

with open(temp_file.name, "w") as f:
    f.write(input_code)

newground_out_of_time = False
newground_output = None
second_grounder_output = None
solver_output = None

newground_clingo_duration = timeout

grounding_file_size_kb = 0

newground_process_p = subprocess.Popen([config["python_command"], "start_newground.py", config["rewriting_strategy"],  f"{temp_file.name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

if grounder == "NEWGROUND-IDLV":
    grounder_process_p = subprocess.Popen([config["idlv_command"], f"--stdin"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
elif grounder == "NEWGROUND-GRINGO":
    grounder_process_p = subprocess.Popen([config["gringo_command"]], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

solver_process_p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory) 

newground_start_time = time.time()   

try: 
    newground_output = newground_process_p.communicate( timeout = timeout)[0]
    newground_duration = time.time() - newground_start_time

    newground_output = newground_output.decode().strip().encode()

    if newground_process_p.returncode != 0:
        #print("return code != 0")
        newground_out_of_time = True
        newground_duration = timeout

except TimeoutExpired:
    newground_process_p.kill()
    newground_output, failure_errors = newground_process_p.communicate()

    newground_out_of_time = True
    newground_duration = timeout

except Exception as ex:
    #print(StartBenchmarkUtils.encode_argument(str(ex)))
    newground_out_of_time = True
    newground_duration = timeout

if newground_output != None:
    grounding_file_size_bytes = len(newground_output)
    grounding_file_size_kb = grounding_file_size_bytes / 1024

grounder_start = time.time()

if newground_output != None and newground_out_of_time == False and newground_duration < timeout:
    try:

        second_grounder_output = grounder_process_p.communicate(input = newground_output, timeout = timeout)[0]
        newground_duration = (time.time() - grounder_start) + newground_duration

        second_grounder_output = second_grounder_output.decode().strip().encode()

        if grounder_process_p.returncode != 0:
            #print("other bad things")
            newground_out_of_time = True
            newground_duration = timeout

    except TimeoutExpired:
        grounder_process_p.kill()
        second_grounder_output, failure_errors = grounder_process_p.communicate()

        newground_out_of_time = True
        newground_duration = timeout


    except Exception as ex:
        #print(ex)
        newground_out_of_time = True
        newground_duration = timeout

    if second_grounder_output != None:
        grounding_file_size_bytes = len(second_grounder_output)
        grounding_file_size_kb = grounding_file_size_bytes / 1024

    solver_start_time = time.time()

    if second_grounder_output != None and newground_out_of_time == False and newground_duration < timeout and ground_and_solve:

        try:

            solver_output = solver_process_p.communicate(input = second_grounder_output, timeout = (timeout - newground_duration))[0]
            clingo_end_time = time.time()   
            newground_clingo_duration = clingo_end_time - solver_start_time + newground_duration

            if solver_process_p.returncode != 10 and solver_process_p.returncode != 20: # Clingo return code for everything fine
                #print("clingo bad things")
                newground_out_of_time = True
                newground_clingo_duration = timeout

            #print(solver_output.decode().strip())

        except TimeoutExpired:
            solver_process_p.kill()
            solver_output, errs = solver_process_p.communicate()
            clingo_end_time = time.time()   

            newground_out_of_time = True
            newground_clingo_duration = timeout

        except Exception as ex:
            #print(ex)
            newground_out_of_time = True
            newground_clingo_duration = timeout
    else:
        newground_out_of_time = True
        newground_clingo_duration = timeout

else:
    newground_out_of_time = True
    newground_duration = timeout


print(StartBenchmarkUtils.encode_argument((newground_out_of_time, newground_clingo_duration, newground_duration, grounding_file_size_kb)))

sys.exit(0)
