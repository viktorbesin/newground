import sys
import random

mx = int(sys.argv[1])
prob = int(sys.argv[2])

assert(prob >= 0)
assert(prob <= 100)

for i in range(1,mx):
	for j in range(1,mx):
		if random.randint(0,100) <= prob:
			print("edge({0},{1}).".format(i,j))
