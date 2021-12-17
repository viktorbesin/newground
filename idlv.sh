#../I-DLV/idlv_1.1.6_linux_x86-64 --print-rewriting --output 1 $1 #instances/grounding-issue4.lp
./noclingo.sh $1 | cat - $2 | ../I-DLV/idlv_1.1.6_linux_x86-64 --output 1 /dev/stdin #instances/grounding-issue4.lp
