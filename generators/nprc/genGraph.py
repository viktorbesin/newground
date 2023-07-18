import sys
import random

def gen_graph(grid_size, horizontal_no_edge_probability, vertical_no_edge_probability, diagonal_no_edge_probability):

    vertices = []
    edges = []

    for y in range(0, grid_size ):
        for x in range(1, grid_size + 1):
            vertex_index = y*grid_size+x
            vertices.append(f"vertex({vertex_index}).\n")

            if x > 1 and random.randint(0,100) >= horizontal_no_edge_probability: 
                # Left neighbor
                edges.append(f"edge({vertex_index - 1}, {vertex_index}).\n")

            if y > 0 and random.randint(0,100) >= vertical_no_edge_probability:
                # Upper neighbor
                edges.append(f"edge({vertex_index - grid_size}, {vertex_index}).\n")

            if y > 0 and x > 1 and random.randint(0,100) >= diagonal_no_edge_probability:
                # Left Diag Neighbor
                edges.append(f"edge({vertex_index - grid_size - 1}, {vertex_index}).\n")

            if y > 0 and x < grid_size and random.randint(0,100) >= diagonal_no_edge_probability:
                # Right Diag Neighbor
                edges.append(f"edge({vertex_index - grid_size + 1}, {vertex_index}).\n")

    return (vertices, edges)

if __name__ == '__main__':
    print("START WITH genGraphs.py")
