#!/bin/bash
for d in `seq -w 070 10 100`
do
	nohup /home/thinklex/newground/start_benchmark_tests.py generators/nprc/density_benchmarks/${d}_density benchmark_output_nprc_with_aggregates_${d}_density &> log_nprc_with_aggregates_${d}_density &
done
