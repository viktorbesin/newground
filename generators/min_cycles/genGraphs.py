import sys

from genGraph import gen_graph

if __name__ == '__main__':

    horizontal_no_edge_probability = int(sys.argv[1])
    vertical_no_edge_probability = int(sys.argv[2])
    diagonal_no_edge_probability = int(sys.argv[3])

    for grid_size in range(3,100,1):

        vertices, edges = gen_graph(grid_size, horizontal_no_edge_probability, vertical_no_edge_probability, diagonal_no_edge_probability)

        write_string = ""
        for vertex in vertices:
            write_string += vertex

        for edge in edges:
            write_string += edge

        write_string += f"min_reached_vertices({int(len(vertices) * 0.75)})."

        file_name = ""

        if grid_size < 10:
            file_name =f"instance_000{grid_size}.lp"
        elif grid_size < 100:
            file_name =f"instance_00{grid_size}.lp"
        elif grid_size < 1000:
            file_name =f"instance_0{grid_size}.lp"
        else:
            file_name =f"instance_{grid_size}.lp"

        f = open(file_name, "w")

        f.write(write_string)

        f.close()


