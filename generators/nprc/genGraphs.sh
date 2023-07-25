mkdir density_benchmarks

for d in `seq -w 010 10 100`
do
	mkdir density_benchmarks/${d}_density

	for j in `seq -w 0020 40 300` 
	do
		echo "size $j"
			../../python3 genOldGraph.py $j $d > density_benchmarks/${d}_density/instance_${j}.lp
	done
	for j in `seq -w 0310 10 450` 
	do
		echo "size $j"
			../../python3 genOldGraph.py $j $d > density_benchmarks/${d}_density/instance_${j}.lp
	done

	cp additional_instance.lp density_benchmarks/${d}_density/additional_instance.lp
	cp encoding.lp density_benchmarks/${d}_density/encoding.lp
done
