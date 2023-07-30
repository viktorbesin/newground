import sys
import base64
import json
import pickle

import os
import io
import re

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

mockup = False

if mockup == False:
    config = StartBenchmarkUtils.decode_argument(sys.argv[1])
    timeout = StartBenchmarkUtils.decode_argument(sys.argv[2])
    ground_and_solve = StartBenchmarkUtils.decode_argument(sys.argv[3])
    grounder = StartBenchmarkUtils.decode_argument(sys.argv[4])
    optimization_benchmarks = StartBenchmarkUtils.decode_argument(sys.argv[5])

    input_code = sys.stdin.read()
else:
    config = {}
    config["clingo_command"] = "./clingo"
    config["gringo_command"] = "./gringo"
    config["idlv_command"] = "./idlv.bin"
    config["python_command"] = "./python3"
    config["rewriting_strategy"] = "--aggregate-strategy=replace"

    timeout = 1800
    ground_and_solve = True
    grounder = "NEWGROUND-GRINGO"
    optimization_benchmarks = True

    input_code = "bliblablaume"

temp_file = tempfile.NamedTemporaryFile("w+")

with open(temp_file.name, "w") as f:
    f.write(input_code)

newground_out_of_time = False
newground_output = None
second_grounder_output = None
solver_output = None

newground_clingo_duration = timeout

grounding_file_size_kb = 0

newground_args = [config["python_command"], "start_newground.py", config["rewriting_strategy"],  f"{temp_file.name}"]

if optimization_benchmarks == False:
    if grounder == "NEWGROUND-IDLV":
        grounder_args = [config["idlv_command"], f"--stdin"]
    elif grounder == "NEWGROUND-GRINGO":
        grounder_args = [config["gringo_command"]]

    solver_args = [config["clingo_command"], "--mode=clasp"]
else:
    if grounder == "NEWGROUND-IDLV":
        grounder_args = [config["idlv_command"], f"--stdin", "--output=1"]
    elif grounder == "NEWGROUND-GRINGO":
        grounder_args = [config["gringo_command"]]

    solver_args = [config["clingo_command"]]


newground_process_p = subprocess.Popen(newground_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

grounder_process_p = subprocess.Popen(grounder_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)   
solver_process_p = subprocess.Popen(solver_args, stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory) 

newground_start_time = time.time()   

try: 
    newground_output = newground_process_p.communicate( timeout = timeout)[0]
    newground_duration = time.time() - newground_start_time
        
    newground_output = newground_output.decode().strip().encode()

    if newground_process_p.returncode != 0:
        newground_out_of_time = True
        newground_duration = timeout

except TimeoutExpired:
    newground_process_p.kill()
    newground_output, failure_errors = newground_process_p.communicate()

    newground_out_of_time = True
    newground_duration = timeout

except Exception as ex:
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
            newground_out_of_time = True
            newground_duration = timeout

    except TimeoutExpired:
        grounder_process_p.kill()
        second_grounder_output, failure_errors = grounder_process_p.communicate()


        newground_out_of_time = True
        newground_duration = timeout


    except Exception as ex:
        newground_out_of_time = True
        newground_duration = timeout

    if second_grounder_output != None:
        grounding_file_size_bytes = len(second_grounder_output)
        grounding_file_size_kb = grounding_file_size_bytes / 1024

    solver_start_time = time.time()

    if second_grounder_output != None and newground_out_of_time == False and newground_duration < timeout and ground_and_solve:

        if optimization_benchmarks:
            second_grounder_output = (re.sub(r"Aux", r"aux", second_grounder_output.decode())).encode()
        
        solver_start_time = time.time() #Restart solver start time as potential regex duration is too long

        try:

            solver_output = solver_process_p.communicate(input = second_grounder_output, timeout = (timeout - newground_duration))[0]


            clingo_end_time = time.time()   
            newground_clingo_duration = clingo_end_time - solver_start_time + newground_duration

            if solver_process_p.returncode != 10 and solver_process_p.returncode != 20 and solver_process_p.returncode != 30:
                newground_out_of_time = True
                newground_clingo_duration = timeout


        except TimeoutExpired:
            solver_process_p.kill()
            solver_output, errs = solver_process_p.communicate()
            clingo_end_time = time.time()   

            newground_out_of_time = True
            newground_clingo_duration = timeout

        except Exception as ex:
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
