import sys
import random

mx = int(sys.argv[1])
prob = int(sys.argv[2])

assert(prob >= 0)
assert(prob <= 100)

for i in range(1,mx):
	for j in range(1,mx):
		if random.randint(0,100) <= prob:
			print("manAssignsScore({0},{1},{2}).".format(i,j, random.randint(0,int(mx/10.0))))
		if random.randint(0,100) <= prob:
			print("womanAssignsScore({0},{1},{2}).".format(i,j,random.randint(0,int(mx/10.0))))
