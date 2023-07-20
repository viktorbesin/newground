for i in `seq -w 005 25 100`
do
	echo "density ${i}"
	nohup /home/thinklex/newground/start_benchmark_tests.py generators/marriages/instances/graph_density_${i} benchmark_output_sm_${i} &
done
