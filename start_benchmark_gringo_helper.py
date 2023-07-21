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

instance_file_contents = StartBenchmarkUtils.decode_argument(sys.argv[1])
encoding_file_contents = StartBenchmarkUtils.decode_argument(sys.argv[2])
config = StartBenchmarkUtils.decode_argument(sys.argv[3])
timeout = StartBenchmarkUtils.decode_argument(sys.argv[4])
ground_and_solve = StartBenchmarkUtils.decode_argument(sys.argv[5])
grounder = StartBenchmarkUtils.decode_argument(sys.argv[6])


clingo_out_of_time = False
temp_file = tempfile.NamedTemporaryFile("w+")

with open(temp_file.name, "w") as f:
    f.write(instance_file_contents + encoding_file_contents)

gringo_start_time = time.time()   

try:
    p = subprocess.Popen([config["gringo_command"], f"{temp_file.name}"], stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
    output = p.communicate( timeout = timeout)[0]
    output = output.decode().strip().encode()



    gringo_duration = time.time() - gringo_start_time

    if p.returncode != 0:
        clingo_out_of_time = True
        gringo_duration = timeout

except Exception as ex:
    #print(ex)
    clingo_out_of_time = True
    gringo_duration = timeout


clingo_start_time = time.time()

if output != None and clingo_out_of_time == False and gringo_duration < timeout and ground_and_solve:

    grounding_file_size_bytes = len(output)
    grounding_file_size_kb = grounding_file_size_bytes / 1024

    try:
        p = subprocess.Popen([config["clingo_command"],"--mode=clasp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
        output = p.communicate(timeout = (timeout - gringo_duration),input = output)[0]

        if p.returncode != 10 and p.returncode != 20:
            clingo_out_of_time = True
            gringo_duration = timeout

        #print(output.decode().strip())
    except Exception as ex:
        #print(ex)
        clingo_out_of_time = True

clingo_end_time = time.time()   
gringo_clingo_duration = clingo_end_time - clingo_start_time + gringo_duration

print(StartBenchmarkUtils.encode_argument((clingo_out_of_time, gringo_clingo_duration, gringo_duration, grounding_file_size_kb)))

