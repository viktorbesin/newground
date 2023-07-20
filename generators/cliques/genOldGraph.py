import sys
import random

def gen_graph(mx, prob):
    assert(prob >= 0)
    assert(prob <= 100)

    vertices = []
    edges = []

    for i in range(1,mx):
        vertices.append(f"vertex({i}).")
        for j in range(1,mx):
            if random.randint(0,100) <= prob:
                edges.append("edge({0},{1}).".format(i,j))

    return (vertices, edges)

if __name__ == '__main__':

    mx = int(sys.argv[1])
    prob = int(sys.argv[2])

    vertices, edges = gen_graph(mx, prob)

    for vertex in vertices:
        print(vertex)

    for edge in edges:
        print(edge)

