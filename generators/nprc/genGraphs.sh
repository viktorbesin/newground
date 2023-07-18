rm -r instances
mkdir instances
echo "density $i"
mkdir instances/graph_density_${i}
for j in `seq -w 010 5 200` 
do
	echo "size $j"
		../../python3 genOldGraph.py $j 100 > instances/instance_${j}.lp
done

cp additional_instance.lp instances/additional_instance.lp
cp encoding.lp instances/encoding.lp

