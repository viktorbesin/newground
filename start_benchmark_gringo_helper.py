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

from sys import stdin

from start_benchmark_utils import StartBenchmarkUtils

def limit_virtual_memory():
    max_virtual_memory = 1024 * 1024 * 1024 * 32 # 32GB

    # TUPLE -> (soft limit, hard limit)
    resource.setrlimit(resource.RLIMIT_AS, (max_virtual_memory, max_virtual_memory))

config = StartBenchmarkUtils.decode_argument(sys.argv[1])
timeout = StartBenchmarkUtils.decode_argument(sys.argv[2])
ground_and_solve = StartBenchmarkUtils.decode_argument(sys.argv[3])
grounder = StartBenchmarkUtils.decode_argument(sys.argv[4])
optimization_benchmarks = StartBenchmarkUtils.decode_argument(sys.argv[5])

input_code = sys.stdin.read()

clingo_out_of_time = False
grounder_output = None
solver_output = None

gringo_clingo_duration = timeout

temp_file = tempfile.NamedTemporaryFile("w+")

with open(temp_file.name, "w") as f:
    f.write(input_code)
    #f.write(instance_file_contents + encoding_file_contents)

gringo_start_time = time.time()   


if optimization_benchmarks == False:
    grounder_args = [config["gringo_command"], f"{temp_file.name}"]
    solver_args = [config["clingo_command"], "--mode=clasp"]
else:
    grounder_args = [config["gringo_command"], "--text", f"{temp_file.name}"]
    solver_args = [config["clingo_command"]]

grounder_process_p = subprocess.Popen(grounder_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)   
solver_process_p = subprocess.Popen(solver_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

try:
    grounder_output = grounder_process_p.communicate( timeout = timeout)[0]
    gringo_duration = time.time() - gringo_start_time

    grounder_output = grounder_output.decode().strip().encode()

    if grounder_process_p.returncode != 0:
        clingo_out_of_time = True
        gringo_duration = timeout

except TimeoutExpired:
    grounder_process_p.kill()
    grounder_output, failure_errors = grounder_process_p.communicate()

    gringo_duration = timeout
    clingo_out_of_time = True

except Exception as ex:
    clingo_out_of_time = True
    gringo_duration = timeout

if grounder_output != None:
    grounding_file_size_bytes = len(grounder_output)
    grounding_file_size_kb = grounding_file_size_bytes / 1024

clingo_start_time = time.time()


if grounder_output != None and clingo_out_of_time == False and gringo_duration < timeout and ground_and_solve:
    try:
        (solver_output, solver_error) = solver_process_p.communicate(timeout = (timeout - gringo_duration),input = grounder_output)

        clingo_end_time = time.time()   
        gringo_clingo_duration = clingo_end_time - clingo_start_time + gringo_duration

        if solver_process_p.returncode != 10 and solver_process_p.returncode != 20 and solver_process_p.returncode != 30:
            clingo_out_of_time = True
            gringo_clingo_duration = timeout

    except TimeoutExpired:
        solver_process_p.kill()
        solver_output, errs = solver_process_p.communicate()

        clingo_out_of_time = True
        gringo_clingo_duration = timeout

    except Exception as ex:
        clingo_out_of_time = True
        gringo_clingo_duration = timeout
else:
    clingo_out_of_time = True
    gringo_clingo_duration = timeout
 
        
print(StartBenchmarkUtils.encode_argument((clingo_out_of_time, gringo_clingo_duration, gringo_duration, grounding_file_size_kb)))

sys.exit(0)
