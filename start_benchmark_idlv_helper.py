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

idlv_out_of_time = False
grounder_output = None
solver_output = None

idlv_clingo_duration = timeout

grounding_file_size_kb = 0

temp_file = tempfile.NamedTemporaryFile(mode="w+")

with open(temp_file.name, "w") as f:
    f.write(input_code)

grounder_process_p = subprocess.Popen([config["idlv_command"], f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
solver_process_p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory) 
idlv_start_time = time.time()   

try:
    grounder_output = grounder_process_p.communicate( timeout = timeout)[0]
    idlv_duration = time.time() - idlv_start_time

    grounder_output = grounder_output.decode().strip().encode()

    if grounder_process_p.returncode != 0:
        idlv_out_of_time = True
        idlv_duration = timeout

except TimeoutExpired:
    grounder_process_p.kill()
    grounder_output, failure_errors = grounder_process_p.communicate()

    idlv_out_of_time = True
    idlv_duration = timeout

except Exception as ex:
    #print(ex)
    idlv_out_of_time = True
    idlv_duration = timeout

if grounder_output != None:
    grounding_file_size_bytes = len(grounder_output)
    grounding_file_size_kb = grounding_file_size_bytes / 1024

clingo_start_time = time.time()

if grounder_output != None and idlv_out_of_time == False and idlv_duration < timeout and ground_and_solve:

    try:
        solver_output = solver_process_p.communicate(input = grounder_output, timeout = (timeout - idlv_duration))[0]

        clingo_end_time = time.time()   
        idlv_clingo_duration = clingo_end_time - clingo_start_time + idlv_duration

        if solver_process_p.returncode != 10 and solver_process_p.returncode != 20:
            idlv_out_of_time = True
            idlv_clingo_duration = timeout

    except TimeoutExpired:
        solver_process_p.kill()
        solver_output, failure_errors = solver_process_p.communicate()

        idlv_out_of_time = True
        idlv_clingo_duration = timeout

    except Exception as ex:
        #print(ex)
        idlv_out_of_time = True
        idlv_clingo_duration = timeout
else:
    idlv_out_of_time = True
    idlv_clingo_duration = timeout


print(StartBenchmarkUtils.encode_argument((idlv_out_of_time, idlv_clingo_duration, idlv_duration, grounding_file_size_kb)))

sys.exit(0)
