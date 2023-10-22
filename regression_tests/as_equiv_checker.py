import os
import sys
import argparse
import subprocess
import resource

import clingo

from hybrid_grounding.hybrid_grounding import HybridGrounding
from hybrid_grounding.default_output_printer import DefaultOutputPrinter

from hybrid_grounding.aggregate_strategies.aggregate_mode import AggregateMode

from hybrid_grounding.cyclic_strategy import CyclicStrategy

from hybrid_grounding.grounding_modes import GroundingModes

from .regression_test_mode import RegressionTestStrategy

def limit_virtual_memory():
    max_virtual_memory = 1024 * 1024 * 1024 * 64 # 64GB

    # TUPLE -> (soft limit, hard limit)
    resource.setrlimit(resource.RLIMIT_AS, (max_virtual_memory, max_virtual_memory))


def block_print():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

class CustomOutputPrinter(DefaultOutputPrinter):

    def __init__(self):
        self.string = ""

    def custom_print(self, string):
        self.string = self.string + str(string) + '\n'

    def get_string(self):
        return self.string

class Context:
    def id(self, x):
        return x

    def seq(self, x, y):
        return [x, y]

class EquivChecker:

    def __init__(self, chosenRegressionTestMode):
        self.chosenRegressiontestMode = chosenRegressionTestMode
        self.clingo_output = []
        self.hybrid_grounding_output = []

        self.clingo_hashes = {}
        self.hybrid_grounding_hashes = {}

    def on_model(self, m, output, hashes):
        symbols = m.symbols(shown=True)
        output.append([])
        cur_pos = len(output) - 1
        for symbol in symbols:
            output[cur_pos].append(str(symbol))

        output[cur_pos].sort()

        hashes[(hash(tuple(output[cur_pos])))] = cur_pos

    def parse(self):
        parser = argparse.ArgumentParser(prog='Answerset Equivalence Checker', description='Checks equivalence of answersets produced by hybrid_grounding and clingo.')

        parser.add_argument('instance')
        parser.add_argument('encoding')
        args = parser.parse_args()

        instance_filename = args.instance
        encoding_filename = args.encoding

        if not os.path.isfile(instance_filename):
            print(f'Provided instance file \'{instance_filename}\' not found or is not a file')
            return
        if not os.path.isfile(encoding_filename):
            print(f'Provided encoding file \'{encoding_filename}\' not found or is not a file')
            return

        instance_file_contents = open(instance_filename, 'r').read()
        encoding_file_contents = open(encoding_filename, 'r').read()

        return (instance_file_contents, encoding_file_contents)



    def start(self, instance_file_contents, encoding_file_contents, verbose = True, one_directional_equivalence = True):
        """ 
            one_directional_equivalence: If True, then only the direction clingo -> hybrid_grounding is checked, i.e. it must be the case, that for each answer set in the clingo result, there must be one in the hybrid_grounding result as well (but therefore it could be, that hybrid_grounding has more answersets)
        """

        regression_test_strategy_string = ""

        if self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RS_STAR or self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RS_PLUS or self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RS or self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RA or self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RECURSIVE:
            grounding_mode = GroundingModes.REWRITE_AGGREGATES_NO_GROUND
            cyclic_strategy = CyclicStrategy.ASSUME_TIGHT
            ground_guess = False

            regression_test_strategy_string = "Checking Aggregates "

            if self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RS_STAR:
                aggregate_modes = [
                    ("RS-STAR", AggregateMode.RS_STAR)
                ]
                regression_test_strategy_string += "with RS-STAR strategy"
            elif self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RS_PLUS:
                aggregate_modes = [
                    ("RS-PLUS", AggregateMode.RS_PLUS)
                ]
                regression_test_strategy_string += "with RS-PLUS strategy"
            elif self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RS:
                aggregate_modes = [
                    ("RS", AggregateMode.RS)
                ]
                regression_test_strategy_string += "with RS strategy"
            elif self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RA:
                aggregate_modes = [
                    ("RA", AggregateMode.RA)
                ]
                regression_test_strategy_string += "with RA strategy"
            elif self.chosenRegressiontestMode == RegressionTestStrategy.AGGREGATES_RECURSIVE:
                aggregate_modes = [
                    ("RECURSIVE", AggregateMode.RECURSIVE)
                ]
                regression_test_strategy_string += "with Recursive strategy"


        elif self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_TIGHT or self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_SHARED_CYCLE or self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS_AAAI or self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS: 
            aggregate_modes = [("RA", AggregateMode.RA)]
            grounding_mode = GroundingModes.REWRITE_AGGREGATES_GROUND_PARTLY
            ground_guess = False

            regression_test_strategy_string = "Checking HybridGrounding with partly rewriting "

            if self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_TIGHT:
                cyclic_strategy = CyclicStrategy.ASSUME_TIGHT
                regression_test_strategy_string += " with the assumption of tight programs."
            elif self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_SHARED_CYCLE:
                cyclic_strategy = CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES
                regression_test_strategy_string += " with the rewriting-shared-cycle strategy for normal programs."
            elif self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS_AAAI:
                cyclic_strategy = CyclicStrategy.LEVEL_MAPPING_AAAI
                regression_test_strategy_string += " with the level-mappings rewriting 1."
            elif self.chosenRegressiontestMode == RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS:
                cyclic_strategy = CyclicStrategy.LEVEL_MAPPING
                regression_test_strategy_string += " with the level-mappings rewriting 2."

        elif self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_TIGHT or  self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_SHARED_CYCLE or self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS_AAAI or self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS:
        
            aggregate_modes = [("RA", AggregateMode.RA)]
            grounding_mode = GroundingModes.REWRITE_AGGREGATES_GROUND_FULLY
            ground_guess = True

            regression_test_strategy_string = "Checking HybridGrounding with fully rewriting "

            if self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_TIGHT:
                cyclic_strategy = CyclicStrategy.ASSUME_TIGHT
                regression_test_strategy_string += " with the assumption of tight programs."
            elif self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_SHARED_CYCLE:
                cyclic_strategy = CyclicStrategy.SHARED_CYCLE_BODY_PREDICATES
                regression_test_strategy_string += " with the rewriting-shared-cycle strategy for normal programs."
            elif self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS_AAAI:
                cyclic_strategy = CyclicStrategy.LEVEL_MAPPING_AAAI
                regression_test_strategy_string += " with the level-mappings rewriting 1."
            elif self.chosenRegressiontestMode == RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS:
                cyclic_strategy = CyclicStrategy.LEVEL_MAPPING
                regression_test_strategy_string += " with the level-mappings rewriting 2."
        else:
            raise Exception("REGRESSION TEST STRATEGY NOT IMPLEMENTED")

        print("<<<<<<<<<<>>>>>>>>>>")
        print(f"---- {regression_test_strategy_string} ----")
        print("<<<<<<<<<<>>>>>>>>>>")

        works = True
        no_show = False

        for aggregate_mode in aggregate_modes:

            print(f"[INFO] Checking current test with aggregate strategy: {aggregate_mode[0]}")

            combined_file_input = instance_file_contents + encoding_file_contents
            total_content = instance_file_contents + "\n#program rules.\n" + encoding_file_contents
            self.start_clingo(combined_file_input, self.clingo_output, self.clingo_hashes)

            custom_printer = CustomOutputPrinter()

            hybrid_grounding = HybridGrounding(no_show = no_show, ground_guess = ground_guess, output_printer = custom_printer, aggregate_mode = aggregate_mode[1], cyclic_strategy=cyclic_strategy, grounding_mode=grounding_mode)
            hybrid_grounding.start(total_content)
            
            self.start_clingo(custom_printer.get_string(), self.hybrid_grounding_output, self.hybrid_grounding_hashes)

            if not one_directional_equivalence and len(self.clingo_output) != len(self.hybrid_grounding_output):
                works = False
            else:
                for clingo_key in self.clingo_hashes.keys():
                    if clingo_key not in self.hybrid_grounding_hashes:
                        works = False
                        if verbose:
                            print(f"[ERROR] Used Aggregate Mode: {aggregate_mode[0]} - Could not find corresponding stable model in hybrid_grounding for hash {clingo_key}")
                            print(f"[ERROR] This corresponds to the answer set: ")
                            print(self.clingo_output[self.clingo_hashes[clingo_key]])
                            print("Output of HybridGrounding:")
                            print(self.hybrid_grounding_output)

                for hybrid_grounding_key in self.hybrid_grounding_hashes.keys():
                    if hybrid_grounding_key not in self.clingo_hashes:
                        works = False
                        if verbose:
                            print(f"[ERROR] Used Aggregate Mode: {aggregate_mode[0]} - Could not find corresponding stable model in clingo for hash {hybrid_grounding_key}")
                            print(f"[ERROR] This corresponds to the answer set: ")
                            print(self.hybrid_grounding_output[self.hybrid_grounding_hashes[hybrid_grounding_key]])
                            print("Output of HybridGrounding:")
                            print(self.hybrid_grounding_output)


        if not works:
            if verbose:
                print("[INFO] ----------------------")
                print("[INFO] ----------------------")
                print("[INFO] ----------------------")
                print("[INFO] The answersets DIFFER!")
                print(f"[INFO] Clingo produced a total of {len(self.clingo_output)}")
                print(f"[INFO] hybrid_grounding produced a total of {len(self.hybrid_grounding_output)}")

            return (False, len(self.clingo_output), len(self.hybrid_grounding_output))
        else: # works
            if verbose:
                print("[INFO] The answersets are the SAME!")

            return (True, len(self.clingo_output), len(self.hybrid_grounding_output))
        
    
    def start_clingo(self, program_input, output, hashes, timeout=1800):

        arguments = ["clingo", "--project", "--model=0"]

        try:
            #p = subprocess.Popen(arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
            p = subprocess.Popen(arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limit_virtual_memory)       
            (ret_vals_encoded, error_vals_encoded) = p.communicate(input=bytes(program_input, "ascii"), timeout = timeout)

            decoded_string = ret_vals_encoded.decode()

            self.parse_clingo_output(decoded_string, output, hashes)

            if p.returncode != 0 and p.returncode != 10 and p.returncode != 20 and p.returncode != 30:
                print(f">>>>> Other return code than 0 in helper: {p.returncode}")

        except Exception as ex:
            try:
                p.kill()
            except Exception as e:
                pass

            print(ex)

    def parse_clingo_output(self, output_string, output, hashes):

        next_line_model = False

        splits = output_string.split("\n")
        index = 0
        for line in splits:

            if next_line_model == True:

                splits_space = line.split(" ")
                splits_space.sort()

                output.append([])
                cur_pos = len(output) - 1
                output[cur_pos] = splits_space
                hashes[(hash(tuple(output[cur_pos])))] = cur_pos

                next_line_model = False

            if line.startswith("Answer"):
                next_line_model = True


            index = index + 1