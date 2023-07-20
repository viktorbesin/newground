rm -r instances
mkdir instances

for j in `seq -w 0330 2 350` 
do
	echo "size $j"
		../../python3 genOldGraph.py $j 100 > instances/instance_${j}.lp
done

cp additional_instance.lp instances/additional_instance.lp
cp encoding.lp instances/encoding.lp
