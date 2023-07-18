rm -r instances
mkdir instances

mkdir instances
for i in `seq -w 005 5 100`
do
	echo "density $i"
	mkdir instances/graph_density_${i}
	for j in `seq -w 010 10 200` 
	do
		echo "size $j, density $i"
			../../python3 genMarriage.py $j $i > instances/graph_density_${i}/instance_${j}.lp
	done

	cp additional_instance.lp instances/graph_density_${i}/additional_instance.lp
	cp encoding.lp instances/graph_density_${i}/encoding.lp
done


