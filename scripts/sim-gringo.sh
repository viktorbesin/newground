$(dirname "$0")/noclingo.sh $1 | cat - $2 | gringo --verbose=2 --output text | wc
