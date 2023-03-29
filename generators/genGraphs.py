import sys

from genGraph import gen_graph

if __name__ == '__main__':

    prob = int(sys.argv[1])

    assert(prob >= 0)
    assert(prob <= 100)

    for i in range(4,101,3):
        vertices, edges = gen_graph(i, prob)

        write_string = ""
        for vertex in vertices:
            write_string += vertex

        for edge in edges:
            write_string += edge

        file_name = ""

        if i < 10:
            file_name =f"instance_00{i}.lp"
        elif i < 100:
            file_name =f"instance_0{i}.lp"
        else:
            file_name =f"instance_{i}.lp"

        f = open(file_name, "w")

        f.write(write_string)

        f.close()


