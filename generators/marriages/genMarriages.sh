for i in `seq 100 10 200` 
do
	for j in `seq 5 5 100`
	do
		echo "size $i, prob $j"
		if [ -f "instances/marriage_graphs/random_${i}_${j}.lp" ]; then
			echo "file exists"
		else
			python3 genMarriage.py $i $j > instances/marriage_graphs/random_${i}_${j}.lp
		fi
	done
done
