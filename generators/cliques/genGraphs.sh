mkdir tmp

for j in `seq -w 1000 10 1500` 
do
	echo "size $j"
		../../python3 genOldGraph.py $j 100 > tmp/instance_${j}.lp
done
