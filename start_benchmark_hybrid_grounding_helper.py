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
    grounder = "hybrid_grounding-GRINGO"
    optimization_benchmarks = True

    input_code = "bliblablaume"

temp_file = tempfile.NamedTemporaryFile("w+")

with open(temp_file.name, "w") as f:
    f.write(input_code)

hybrid_grounding_out_of_time = False
hybrid_grounding_output = None
second_grounder_output = None
solver_output = None

hybrid_grounding_clingo_duration = timeout

grounding_file_size_kb = 0

hybrid_grounding_args = [config["python_command"], "start_hybrid_grounding.py", config["rewriting_strategy"],  f"{temp_file.name}"]

if optimization_benchmarks == False:
    if grounder == "hybrid_grounding-IDLV":
        grounder_args = [config["idlv_command"], f"--stdin"]
    elif grounder == "hybrid_grounding-GRINGO":
        grounder_args = [config["gringo_command"]]

    solver_args = [config["clingo_command"], "--mode=clasp"]
else:
    if grounder == "hybrid_grounding-IDLV":
        grounder_args = [config["idlv_command"], f"--stdin", "--output=1"]
    elif grounder == "hybrid_grounding-GRINGO":
        grounder_args = [config["gringo_command"]]

    solver_args = [config["clingo_command"]]


hybrid_grounding_process_p = subprocess.Popen(hybrid_grounding_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

grounder_process_p = subprocess.Popen(grounder_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)   
solver_process_p = subprocess.Popen(solver_args, stdin=subprocess.PIPE, stdout = subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory) 

hybrid_grounding_start_time = time.time()   

try: 
    hybrid_grounding_output = hybrid_grounding_process_p.communicate( timeout = timeout)[0]
    hybrid_grounding_duration = time.time() - hybrid_grounding_start_time
        
    hybrid_grounding_output = hybrid_grounding_output.decode().strip().encode()

    if hybrid_grounding_process_p.returncode != 0:
        hybrid_grounding_out_of_time = True
        hybrid_grounding_duration = timeout

except TimeoutExpired:
    hybrid_grounding_process_p.kill()
    hybrid_grounding_output, failure_errors = hybrid_grounding_process_p.communicate()

    hybrid_grounding_out_of_time = True
    hybrid_grounding_duration = timeout

except Exception as ex:
    hybrid_grounding_out_of_time = True
    hybrid_grounding_duration = timeout

if hybrid_grounding_output != None:
    grounding_file_size_bytes = len(hybrid_grounding_output)
    grounding_file_size_kb = grounding_file_size_bytes / 1024

grounder_start = time.time()

if hybrid_grounding_output != None and hybrid_grounding_out_of_time == False and hybrid_grounding_duration < timeout:
    try:

        second_grounder_output = grounder_process_p.communicate(input = hybrid_grounding_output, timeout = timeout)[0]
        hybrid_grounding_duration = (time.time() - grounder_start) + hybrid_grounding_duration
        

        second_grounder_output = second_grounder_output.decode().strip().encode()

        if grounder_process_p.returncode != 0:
            hybrid_grounding_out_of_time = True
            hybrid_grounding_duration = timeout

    except TimeoutExpired:
        grounder_process_p.kill()
        second_grounder_output, failure_errors = grounder_process_p.communicate()


        hybrid_grounding_out_of_time = True
        hybrid_grounding_duration = timeout


    except Exception as ex:
        hybrid_grounding_out_of_time = True
        hybrid_grounding_duration = timeout

    if second_grounder_output != None:
        grounding_file_size_bytes = len(second_grounder_output)
        grounding_file_size_kb = grounding_file_size_bytes / 1024

    solver_start_time = time.time()

    if second_grounder_output != None and hybrid_grounding_out_of_time == False and hybrid_grounding_duration < timeout and ground_and_solve:

        if optimization_benchmarks:
            second_grounder_output = (re.sub(r"Aux", r"aux", second_grounder_output.decode())).encode()
        
        solver_start_time = time.time() #Restart solver start time as potential regex duration is too long

        try:

            solver_output = solver_process_p.communicate(input = second_grounder_output, timeout = (timeout - hybrid_grounding_duration))[0]


            clingo_end_time = time.time()   
            hybrid_grounding_clingo_duration = clingo_end_time - solver_start_time + hybrid_grounding_duration

            if solver_process_p.returncode != 10 and solver_process_p.returncode != 20 and solver_process_p.returncode != 30:
                hybrid_grounding_out_of_time = True
                hybrid_grounding_clingo_duration = timeout


        except TimeoutExpired:
            solver_process_p.kill()
            solver_output, errs = solver_process_p.communicate()
            clingo_end_time = time.time()   

            hybrid_grounding_out_of_time = True
            hybrid_grounding_clingo_duration = timeout

        except Exception as ex:
            hybrid_grounding_out_of_time = True
            hybrid_grounding_clingo_duration = timeout
    else:
        hybrid_grounding_out_of_time = True
        hybrid_grounding_clingo_duration = timeout

else:
    hybrid_grounding_out_of_time = True
    hybrid_grounding_duration = timeout


print(StartBenchmarkUtils.encode_argument((hybrid_grounding_out_of_time, hybrid_grounding_clingo_duration, hybrid_grounding_duration, grounding_file_size_kb)))

sys.exit(0)
