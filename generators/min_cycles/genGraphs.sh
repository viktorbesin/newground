rm -r instances
mkdir instances
for i in `seq -w 55 10 55`
do
	echo "density $i"
	mkdir instances/graph_density_${i}
	for j in `seq -w 010 3 200` 
	do
		echo "size $j, density $i"
			../../python3 genOldGraph.py $j $i > instances/graph_density_${i}/instance_${j}.lp
	done

	cp additional_instance.lp instances/graph_density_${i}/additional_instance.lp
	cp encoding.lp instances/graph_density_${i}/encoding.lp
done

