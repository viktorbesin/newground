import argparse
import os
import re
import time

from .as_equiv_checker import EquivChecker

class RegressionTest:
    
    @classmethod
    def start(cls):

        parser = argparse.ArgumentParser(prog='Regression test for Answerset Equivalence Checker', description='Checks equivalence of answersets produced by hybrid_grounding and clingo on all instance-encoding pairs in a subfolder.')

        parser.add_argument('folder')
        args = parser.parse_args()

        folder_path = args.folder 

        sub_directories = []

        sub_folder_pattern = re.compile("^[0-9][0-9]_test$")
        encoding_pattern = re.compile("^encoding_[0-9][0-9]_test\.lp$")
        instance_pattern = re.compile("^instance_[0-9][0-9]_test\.lp$")
        

        for f in os.scandir(folder_path):
            if f.is_dir():
                if sub_folder_pattern.match(str(f.name)):
                    sub_directories.append(str(f.name))
      
        sub_directories.sort()

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

            checker = EquivChecker()
            result, clingo_answersets, hybrid_grounding_answersets = checker.start(instance_file_contents, encoding_file_contents)

            end_time = time.time()

            if result:
                print(f"[INFO] \"{sub}\" test was SUCCESSFUL, clingo-answersets: {clingo_answersets}, hybrid_grounding-answersets: {hybrid_grounding_answersets}")
            else:
                print(f"[INFO] \"{sub}\" test FAILED, clingo-answersets: {clingo_answersets}, hybrid_grounding-answersets: {hybrid_grounding_answersets}")
                failed_tests[sub] = {"clingo_answersets":clingo_answersets, "hybrid_grounding_answersets":hybrid_grounding_answersets}

            total_tests += 1

            print(f"[INFO] \"{sub}\" test took {end_time - start_time} seconds")
                        

     
        print("<<<<---->>>>")
        print("############")
        print("<<<<---->>>>")
        number_failed_tests = len(failed_tests.keys())
        if number_failed_tests > 0:
            print(f"{number_failed_tests}/{total_tests} of executed tests failed:")
            for key in failed_tests.keys():
                print(f"- {key} - Clingo Answersets: {failed_tests[key]['clingo_answersets']}, hybrid_grounding Answersets: {failed_tests[key]['hybrid_grounding_answersets']}")
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

        

