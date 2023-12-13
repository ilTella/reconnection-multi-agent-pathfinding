import math
from .single_agent_planner import a_star, get_sum_of_cost
from .cbs import CBSSolver
from typing import Optional
from pathlib import Path

def get_euclidean_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2)), 2)

def get_shortest_path_length(map: list[list[bool]], start_node: tuple[int, int], goal_node: tuple[int, int], heuristics: dict) -> int:
    path = a_star(map, start_node, goal_node, heuristics, 0, [])
    return len(path) - 1

def print_mapf_instance(map: list[list[bool]], starts: list[tuple[int, int]], goals: Optional[list[tuple[int, int]]] = None) -> None:
    print("Start locations")
    print_locations(map, starts)
    if (goals != None):
        print("Goal locations")
        print_locations(map, goals)

def print_locations(my_map, locations):
    starts_map = [[-1 for _ in range(len(my_map[0]))] for _ in range(len(my_map))]
    for i in range(len(locations)):
        starts_map[locations[i][0]][locations[i][1]] = i
    to_print = ''
    for x in range(len(my_map)):
        for y in range(len(my_map[0])):
            if starts_map[x][y] >= 0:
                to_print += str(starts_map[x][y]) + ' '
            elif my_map[x][y]:
                to_print += '@ '
            else:
                to_print += '. '
        to_print += '\n'
    print(to_print)

def get_cbs_cost(map: list[list[bool]], starts: list[tuple[int, int]], goals: list[tuple[int, int]], shared_var):
    cbs = CBSSolver(map, starts, goals, doPrint=False)
    paths = cbs.find_solution(disjoint=False)
    cost = get_sum_of_cost(paths, goals, starts)
    shared_var.value = cost

def import_mapf_instance(filename):
    f = Path(filename)
    if not f.is_file():
        raise BaseException(filename + " does not exist.")
    f = open(filename, 'r')
    # first line: #rows #columns
    line = f.readline()
    rows, columns = [int(x) for x in line.split(' ')]
    rows = int(rows)
    columns = int(columns)
    # #rows lines with the map
    my_map = []
    for _ in range(rows):
        line = f.readline()
        my_map.append([])
        for cell in line:
            if cell == '@':
                my_map[-1].append(True)
            elif cell == '.':
                my_map[-1].append(False)
    # #agents
    line = f.readline()
    num_agents = int(line)
    # #agents lines with the start/goal positions
    starts = []
    goals = []
    for _ in range(num_agents):
        line = f.readline()
        line_content = line.split(' ')
        if len(line_content) == 2:
            sx, sy = [int(x) for x in line_content]
            starts.append((sx, sy))
        elif  len(line_content) == 4:
            sx, sy, gx, gy = [int(x) for x in line_content]
            starts.append((sx, sy))
            goals.append((gx, gy))
    f.close()
    return my_map, starts, goals