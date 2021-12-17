#../I-DLV/idlv_1.1.6_linux_x86-64 --print-rewriting --output 1 $1 #instances/grounding-issue4.lp
$(dirname "$0")/noclingo.sh $1 | cat - $2 | $(dirname "$0")/idlv_1.1.6_linux_x86-64 --output 1 /dev/stdin | wc #instances/grounding-issue4.lp
