import sys
import base64
import json
import pickle

import os
import io

import time

import subprocess

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

newground_start_time = time.time()   

try: 
    p = subprocess.Popen([config["python_command"], "start_newground.py", config["rewriting_strategy"],  f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

    output = p.communicate( timeout = timeout)[0]
    output = output.decode().strip().encode()

    newground_duration = time.time() - newground_start_time

    if p.returncode != 0:
        #print("return code != 0")
        newground_out_of_time = True
        newground_duration = timeout



except Exception as ex:
    #print(ex)
    newground_out_of_time = True
    newground_duration = timeout


gringo_start = time.time()

if output != None and newground_out_of_time == False and newground_duration < timeout:
    try:
        if grounder == "NEWGROUND-IDLV":
            p = subprocess.Popen([config["idlv_command"], f"--stdin"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

        elif grounder == "NEWGROUND-GRINGO":
            p = subprocess.Popen([config["gringo_command"]], stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=limit_virtual_memory)       

        output = p.communicate(input = output, timeout = timeout)[0]
        output = output.decode().strip().encode()

        newground_duration += (time.time() - gringo_start)

        if p.returncode != 0:
            #print("other bad things")
            newground_out_of_time = True
            newground_duration = timeout

    except Exception as ex:
        #print(ex)
        newground_out_of_time = True
        newground_duration = timeout

clingo_start_time = time.time()

if output != None and newground_out_of_time == False and newground_duration < timeout and ground_and_solve:

    grounding_file_size_bytes = len(output)
    grounding_file_size_kb = grounding_file_size_bytes / 1024

    try:
        p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, preexec_fn=limit_virtual_memory) 

        output = p.communicate(input = output, timeout = (timeout - newground_duration))[0]

        if p.returncode != 10 and p.returncode != 20: # Clingo return code for everything fine
            #print("clingo bad things")
            newground_out_of_time = True
            newground_duration = timeout

        #print(output.decode().strip())

    except Exception as ex:
        #print(ex)
        newground_out_of_time = True
else:
    grounding_file_size_kb = 0

clingo_end_time = time.time()   
newground_clingo_duration = clingo_end_time - clingo_start_time + newground_duration


print(StartBenchmarkUtils.encode_argument((newground_out_of_time, newground_clingo_duration, newground_duration, grounding_file_size_kb)))
    
