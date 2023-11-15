import argparse
import os
import re
import time
import sys

from .as_equiv_checker import EquivChecker
from .regression_test_mode import RegressionTestStrategy

class RegressionTest:
    
    @classmethod
    def start(cls):

        parser = argparse.ArgumentParser(prog='Regression test for Answerset Equivalence Checker', description='Checks equivalence of answersets produced by newground and clingo on all instance-encoding pairs in a subfolder.')

        all_test = "test-all"
        rewriting_modes = [
            RegressionTestStrategy.REWRITING_SHARED_CYCLE,
            RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS,
            RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS_AAAI,
            RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS,
            RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS_AAAI,
            RegressionTestStrategy.FULLY_GROUNDED_SHARED_CYCLE,
        ]

        aggregate_modes = [
            RegressionTestStrategy.AGGREGATES_RS_PLUS,
            RegressionTestStrategy.AGGREGATES_RS_STAR,
            RegressionTestStrategy.AGGREGATES_RA,
            RegressionTestStrategy.AGGREGATES_RS,
            RegressionTestStrategy.AGGREGATES_RECURSIVE
        ]

        regressionTestModes = [
            ("aggregates-rs-star",RegressionTestStrategy.AGGREGATES_RS_STAR),
            ("aggregates-rs-plus",RegressionTestStrategy.AGGREGATES_RS_PLUS),
            ("aggregates-rs",RegressionTestStrategy.AGGREGATES_RS),
            ("aggregates-ra",RegressionTestStrategy.AGGREGATES_RA),
            ("aggregates-recursive",RegressionTestStrategy.AGGREGATES_RECURSIVE),
            ("rewriting-tight",RegressionTestStrategy.REWRITING_TIGHT),
            ("rewriting-shared-cycle",RegressionTestStrategy.REWRITING_SHARED_CYCLE),
            ("rewriting-level-mappings-1",RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS_AAAI),
            ("rewriting-level-mappings-2",RegressionTestStrategy.REWRITING_LEVEL_MAPPINGS),
            ("fully-grounded-tight", RegressionTestStrategy.FULLY_GROUNDED_TIGHT),
            ("fully-grounded-shared-cycle", RegressionTestStrategy.FULLY_GROUNDED_SHARED_CYCLE),
            ("fully-grounded-level-mappings-1", RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS_AAAI),
            ("fully-grounded-level-mappings-2", RegressionTestStrategy.FULLY_GROUNDED_LEVEL_MAPPINGS),
        ]
        parser.add_argument('--mode', choices=[regressionTestMode[0] for regressionTestMode in regressionTestModes] + [all_test], default=regressionTestModes[1][0])
        parser.add_argument('--folder', default="__DEFAULT__")

        args = parser.parse_args()

        chosenRegressionTestMode = None
        for regressionTestMode in regressionTestModes:
            if regressionTestMode[0] == args.mode:
                chosenRegressionTestMode = regressionTestMode[1]
        
        if args.mode == all_test:
            chosenRegressionTestMode = all_test

        folder_path = args.folder 

        if chosenRegressionTestMode != all_test:
            if folder_path == "__DEFAULT__" and chosenRegressionTestMode in rewriting_modes:
                folder_path = os.path.join("regression_tests","tight_non_tight_tests")
            elif folder_path == "__DEFAULT__" and chosenRegressionTestMode in aggregate_modes:
                folder_path = os.path.join("regression_tests","aggregate_tests")

            tests_successfull = cls.regression_test_a_strategy_helper(chosenRegressionTestMode, folder_path)

            if tests_successfull is True:
                sys.exit(0)
            else:
                sys.exit(1)
        else:

            tests_successfull = True

            for aggregate_strategy in aggregate_modes:
                if folder_path == "__DEFAULT__" and aggregate_strategy in aggregate_modes:
                    aggregates_folder = os.path.join("regression_tests","aggregate_tests")
                else:
                    aggregates_folder = folder_path

                test_successful = cls.regression_test_a_strategy_helper(aggregate_strategy, aggregates_folder)
                if not test_successful:
                    strategy_index = regressionTestModes.index(lambda element : element[1] == aggregate_strategy)
                    strategy_string = regressionTestModes[strategy_index][0]
                    print("---------------------------------------------")
                    print(f"The following aggregate-strategy FAILED (responded with an error): {strategy_string}")
                    print("---------------------------------------------")

                tests_successfull = tests_successfull and test_successful

            for rewriting_strategy in rewriting_modes:
                if folder_path == "__DEFAULT__" and rewriting_strategy in rewriting_modes:
                    rewriting_folder = os.path.join("regression_tests","newground_tests")
                else:
                    rewriting_folder = folder_path

                test_successful = cls.regression_test_a_strategy_helper(rewriting_strategy, rewriting_folder)
                if not test_successful:
                    strategy_index = regressionTestModes.index(lambda element : element[1] == rewriting_strategy)
                    strategy_string = regressionTestModes[strategy_index][0]
                    print("---------------------------------------------")
                    print(f"The following rewriting-strategy FAILED (responded with an error): {strategy_string}")
                    print("---------------------------------------------")

                tests_successfull = tests_successfull and test_successful

            if tests_successfull:
                sys.exit(0)
            else:
                sys.exit(1)

    @classmethod
    def regression_test_a_strategy_helper(cls, chosenRegressionTestMode, folder_path):
        sub_directories = []

        sub_folder_pattern = re.compile("^[0-9]{2,3}_test$")
        encoding_pattern = re.compile("^encoding_[0-9]{2,3}_test\.lp$")
        instance_pattern = re.compile("^instance_[0-9]{2,3}_test\.lp$")

        for f in os.scandir(folder_path):
            if f.is_dir():
                if sub_folder_pattern.match(str(f.name)):
                    sub_directories.append(str(f.name))
      
        sub_directories.sort()

        return cls.regression_test_a_strategy(chosenRegressionTestMode, folder_path, sub_directories, encoding_pattern, instance_pattern)

    @classmethod
    def regression_test_a_strategy(cls, chosenRegressionTestMode, folder_path, sub_directories, encoding_pattern, instance_pattern):
        total_tests = 0
        failed_tests = {}
        skipped_tests = {}

        for sub in sub_directories:
            print("<<<<---->>>>")
            print(f"[INFO] \"{sub}\" test is starting")

            path = os.path.join(folder_path, sub)

            encoding_file_name = None
            instance_file_name = None

            for f in os.scandir(path):
                if f.is_file():
                    if encoding_pattern.match(str(f.name)):
                        encoding_file_name = str(f.name)
                    if instance_pattern.match(str(f.name)):
                        instance_file_name = str(f.name)

            if not encoding_file_name:
                print(f"[ERROR] - Could not find encoding-file for sub folder: {sub}.")
                skipped_tests[sub] = "encoding"
                continue
     
            if not instance_file_name:
                print(f"[ERROR] - Could not find instance-file for sub folder: {sub}.")               
                skipped_tests[sub] = "instance"
                continue

            instance_file_contents = open(os.path.join(folder_path, sub, instance_file_name), 'r').read()
            encoding_file_contents = open(os.path.join(folder_path, sub, encoding_file_name), 'r').read()

            start_time = time.time()

            checker = EquivChecker(chosenRegressionTestMode)
            result, clingo_answersets, newground_answersets = checker.start(instance_file_contents, encoding_file_contents)

            end_time = time.time()

            if result:
                print(f"[INFO] \"{sub}\" test was SUCCESSFUL, clingo-answersets: {clingo_answersets}, newground-answersets: {newground_answersets}")
            else:
                print(f"[INFO] \"{sub}\" test FAILED, clingo-answersets: {clingo_answersets}, newground-answersets: {newground_answersets}")
                failed_tests[sub] = {"clingo_answersets":clingo_answersets, "newground_answersets":newground_answersets}

            total_tests += 1

            print(f"[INFO] \"{sub}\" test took {end_time - start_time} seconds")
                        

     
        print("<<<<---->>>>")
        print("############")
        print("<<<<---->>>>")
        number_failed_tests = len(failed_tests.keys())
        if number_failed_tests > 0:
            print(f"{number_failed_tests}/{total_tests} of executed tests failed:")
            for key in failed_tests.keys():
                print(f"- {key} - Clingo Answersets: {failed_tests[key]['clingo_answersets']}, newground Answersets: {failed_tests[key]['newground_answersets']}")
        else:
            print(f"All executed tests were SUCCESSFUL (In total {total_tests} were conducted and {total_tests - len(skipped_tests.keys())} were executed).")

        if len(skipped_tests.keys()) > 0:
            print("############")
            print(f"{len(skipped_tests.keys())} tests were skipped, due to file reading errors:")
            for key in skipped_tests.keys():
                print(f"- {key} - Due to wrong: {skipped_tests[key]}")
        print("<<<<---->>>>")
        print("############")
        print("<<<<---->>>>")

        if number_failed_tests == 0:
            return True
        else:
            return False
        

