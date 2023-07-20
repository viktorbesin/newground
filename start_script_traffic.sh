for i in `seq -w 05 10 35`
do
	echo "density ${i}"
	nohup /home/thinklex/newground/start_benchmark_tests.py generators/traffic_planning_graphs/instances/graph_density_${i} benchmark_output_tpg_${i} &
done
