import sys
import random

def gen_marriage(mx, prob):

    assert(prob >= 0)
    assert(prob <= 100)

    output = []

    for i in range(1,mx):
            for j in range(1,mx):
                    if random.randint(0,100) <= prob:
                        output.append("manAssignsScore({0},{1},{2}).".format(i,j, random.randint(0,int(mx/10.0))))
                    if random.randint(0,100) <= prob:
                        output.append("womanAssignsScore({0},{1},{2}).".format(i,j,random.randint(0,int(mx/10.0))))

    return output

