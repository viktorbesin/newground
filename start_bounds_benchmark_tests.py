#!/home/thinklex/programs/python3.11.3/bin/python3
import os
import sys
import argparse
import time
import subprocess

import re
import multiprocessing

import tempfile

import clingo

from start_benchmark_tests import Benchmark

class BoundsBenchmark:

    def __init__(self):
        # Strategies ->  {replace,rewrite,rewrite-no-body}
        self.rewriting_strategy = "--aggregate-strategy=rewrite-no-body"
        #self.rewriting_strategy = "--aggregate-strategy=rewrite"
        #self.rewriting_strategy = "--aggregate-strategy=replace"



    def parse(self, timeout = None): 

        clingo_mockup = True
        newground_mockup = False
        idlv_mockup = True


        benchmark_helper = Benchmark()

        parser = argparse.ArgumentParser(prog='Primitive Benchmark', description='Benchmarks Newground vs. Clingo (total grounding + solving time).')
        parser.add_argument("outputfilename")
        parser.add_argument("filenames", nargs="+")

        args = parser.parse_args()

        output_filename = args.outputfilename
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

        instance_file_contents = ""

        for file_name in args.filenames:

            f = open(file_name, "r")
            instance_file_contents += f.read() + "\n"


        encoding_first = "c(1) :- "
        encoding_second = "<= #count{A: f(A,B), f(B,C), f(C,D), f(D,E), f(E,F), f(F,G), f(G,H), f(H,I), f(I,A), A != B, A != C, A != D, A != E, A != F, A != G, A != H, A != I, B != C, B != D, B != E, B != F, B != G, B != H, B != I, C != D, C != E, C != F, C != G, C != H, C != I, D != E, D != F, D != G, D != H, D != I, E != F, E != G, E != H, E != I, F != G, F != H, F != I, G != H, G != I, H != I}."

        for lower_bound in range(2,1000,3):

            encoding_file_contents = f"{encoding_first} {lower_bound} {encoding_second}"
            print(encoding_file_contents)

            print("GRINGO")
            if not clingo_mockup:
                gringo_clingo_timeout_occured, gringo_clingo_duration, gringo_duration, gringo_grounding_file_size  = benchmark_helper.clingo_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                gringo_clingo_timeout_occured = False
                gringo_clingo_duration = 0
                gringo_duration = 0
                gringo_grounding_file_size = 0

            print("IDLV")
            if not idlv_mockup:
                idlv_clingo_timeout_occured, idlv_clingo_duration, idlv_duration, idlv_grounding_file_size = benchmark_helper.idlv_benchmark(instance_file_contents, encoding_file_contents, timeout)
            else:
                idlv_clingo_timeout_occured = False
                idlv_clingo_duration = 0
                idlv_duration = 0
                idlv_grounding_file_size = 0

            print("NEWGROUND")
            if not newground_mockup:
                newground_clingo_timeout_occured, newground_clingo_duration, newground_duration, newground_grounding_file_size = benchmark_helper.newground_benchmark(instance_file_contents, encoding_file_contents, timeout)
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
                output_file.write(f"\n{lower_bound},{gringo_clingo_duration},{gringo_clingo_timeout_occured},{idlv_clingo_duration},{idlv_clingo_timeout_occured},{newground_clingo_duration},{newground_clingo_timeout_occured}")


            with open(grounding_time_output_filename, "a") as output_file:
                output_file.write(f"\n{lower_bound},{gringo_duration},{gringo_clingo_timeout_occured},{idlv_duration},{idlv_clingo_timeout_occured},{newground_duration},{newground_clingo_timeout_occured}")

            with open(grounding_size_output_filename, "a") as output_file:
                output_file.write(f"\n{lower_bound},{gringo_grounding_file_size},{gringo_clingo_timeout_occured},{idlv_grounding_file_size},{idlv_clingo_timeout_occured},{newground_grounding_file_size},{newground_clingo_timeout_occured}")





if __name__ == "__main__":
    checker = BoundsBenchmark()

    timeout = 1800
    checker.parse(timeout = timeout)










