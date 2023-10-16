import math
from .enums import ConnectionCriterion
from .single_agent_planner import compute_heuristics
from .utils import get_euclidean_distance, get_shortest_path_length
from pathlib import Path
import re

'''
    'map' and other data structures/functions associated with external libraries use (row, col) to identify nodes,
    while 'connectivity graph' and other data structures/functions in my code use (x, y),
    therefore, when passing arguments to the former, the coordinates must be switched (row = y, col = x)
'''

def are_nodes_a_clique(nodes: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> bool:
    for n1 in nodes:
        for n2 in nodes:
            if (n1 != n2) and (not n2 in connectivity_graph[n1]):
                return False

    return True

def are_nodes_connected(map: list[list[bool]], x1: int, y1: int, x2: int, y2: int, args: list) -> bool:
    connected = False

    if args.connection_criterion == ConnectionCriterion.NONE.name:
        connected = True

    elif args.connection_criterion == ConnectionCriterion.DISTANCE.name:
        if get_euclidean_distance(x1, y1, x2, y2) <= args.connection_distance:
            connected = True

    elif args.connection_criterion == ConnectionCriterion.PATH_LENGTH.name:
        heuristics = compute_heuristics(map, (y2, x2))
        path_len = get_shortest_path_length(map, (y1, x1), (y2, x2), heuristics)
        if path_len <= math.floor(args.connection_distance):
            connected = True

    else:
        raise RuntimeError("Unknown connection criterion: " + args.connection_criterion)
    
    return connected

def generate_connectivity_graph(map: list[list[bool]], args: list) -> dict[tuple[int, int], list[tuple[int, int]]]:
    connectivity_graph = {}

    for row in range(len(map)):
        for col in range(len(map[0])):
            if map[row][col] == False:
                key = (col, row)
                connectivity_graph[key] = []
    
    for key in connectivity_graph.keys():
        x = key[0]
        y = key[1]
        for row in range(len(map)):
            for col in range(len(map[0])):
                if ((x, y) != (col, row)) and (map[row][col] == False):
                    if (are_nodes_connected(map, x, y, col, row, args) == True):
                        connectivity_graph[key].append((col, row))

    return connectivity_graph

def import_connectivity_graph(filename: str) -> dict[tuple[int, int], list[tuple[int, int]]]:
    file = Path(filename)
    if not file.is_file():
        raise BaseException(filename + " does not exist.")
    file = open(filename, 'r')

    connectivity_graph = {}

    while True:
        line = file.readline()
        if not line:
            break
        line_elements = line.split(">")

        key_coords = re.sub("[()]", "", line_elements[0].strip()).split(" ")
        key = (int(key_coords[0]), int(key_coords[1]))

        values = []
        raw_nodes = line_elements[1].strip().split(",")
        for i in range(len(raw_nodes)):
            node_coords = re.sub("[()]", "", raw_nodes[i]).split(" ")
            v = (int(node_coords[0]), int(node_coords[1]))
            values.append(v)
        
        connectivity_graph[key] = values

    return connectivity_graph

def print_connectivity_graph(connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> None: 
    for key in connectivity_graph:
        print(str(key) + " is connected to: " + str(connectivity_graph[key]))