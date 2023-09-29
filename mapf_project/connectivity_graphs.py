import math
from libraries.enums import ConnectionCriterion
from pathlib import Path
import re

FULL_OBSTACLE_WEIGHT = 0.8
PART_OBSTACLE_WEIGHT = 0.2

def get_distance(x1, y1, x2, y2):
    return round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2)), 2)

def consider_obstacles_with_distance(full_obstacles, part_obstacles, distance, debug):
    full_obstacles_weight = round((full_obstacles * FULL_OBSTACLE_WEIGHT), 2)
    part_obstacles_weight = round((part_obstacles * PART_OBSTACLE_WEIGHT), 2)
    result = round((distance + full_obstacles_weight + part_obstacles_weight), 2)
    if debug:
        print("\ttotal distance: (distance) " + str(distance) + " + (full obstacles weight) " + str(full_obstacles_weight) + " + (partial obstacles weight) " + str(part_obstacles_weight) + " = " + str(result))
    return result

def are_vertexes_connected(map, x1, y1, x2, y2, args):
    are_connected = False

    if args.debug:
        print("(" + str(x1) + ", " + str(y1) + ") -> (" + str(x2) + ", " + str(y2) + ")")

    if args.connection_criterion == ConnectionCriterion.NONE.name:
        are_connected = True

    elif args.connection_criterion == ConnectionCriterion.DISTANCE.name:
        if get_distance(x1, y1, x2, y2) <= args.connection_distance:
            are_connected = True

    elif args.connection_criterion == ConnectionCriterion.DISTANCE_AND_OBSTACLES.name:
        full_obstacles = 0
        part_obstacles = 0
        distance = get_distance(x1, y1, x2, y2)

        # case 1: straight line
        if x2 == x1:
            if args.debug:
                print("\tstraight line")
            step = 1
            if y2 < y1: step = -1
            y = y1
            while (y != y2):
                if map[y][x1]: full_obstacles += 1
                y += step
        elif y2 == y1:
            if args.debug:
                print("\tstraight line")
            step = 1
            if x2 < x1: step = -1
            x = x1
            while (x != x2):
                if map[y1][x]: full_obstacles += 1
                x += step

        # case 2: diagonal
        elif math.fabs(x2 - x1) == math.fabs(y2 - y1):
            if args.debug:
                print("\tdiagonal")
            x_step = 1
            if x2 < x1: x_step = -1
            y_step = 1
            if y2 < y1: y_step = -1

            main = [x1, y1]
            main_end = [x2, y2]
            while main[0] != main_end[0] and main[1] != main_end[1]:
                if map[main[1]][main[0]]: full_obstacles += 1
                main[0] += x_step
                main[1] += y_step

            secondary1 = [x1, y1 + y_step]
            secondary1_end = [x2 - x_step, y2]
            while secondary1[0] != secondary1_end[0] + x_step and secondary1[1] != secondary1_end[1] + y_step:
                if map[secondary1[1]][secondary1[0]]: part_obstacles += 1
                secondary1[0] += x_step
                secondary1[1] += y_step

            secondary2 = [x1 + x_step, y1]
            secondary2_end = [x2, y2 - y_step]
            while secondary2[0] != secondary2_end[0] + x_step and secondary2[1] != secondary2_end[1] + y_step:
                if map[secondary2[1]][secondary2[0]]: part_obstacles += 1
                secondary2[0] += x_step
                secondary2[1] += y_step

        # case 3 generic line
        else:
            if args.debug:
                print("\tgeneric line")
            nodes_to_check = []
            x_direction = 1
            if x2 < x1: x_direction = -1
            y_direction = 1
            if y2 < y1: y_direction = -1

            # check nodes around (x1, y1) and (x2, y2)

            if not ((x1, y1 + y_direction) in nodes_to_check):
                nodes_to_check.append((x1, y1 + y_direction))
            if not ((x1 + x_direction, y1) in nodes_to_check):
                nodes_to_check.append((x1 + x_direction, y1))
            corner1 = (x1 + x_direction, y1 + y_direction)
            if not (corner1 in nodes_to_check):
                nodes_to_check.append(corner1)
            
            if not ((x2, y2 - y_direction) in nodes_to_check):
                nodes_to_check.append((x2, y2 - y_direction))
            if not ((x2 - x_direction, y2) in nodes_to_check):
                nodes_to_check.append((x2 - x_direction, y2))
            corner2 = (x2 - x_direction, y2 - y_direction)
            if not (corner2 in nodes_to_check):
                nodes_to_check.append(corner2)

            # check nodes on the line between (x1, y1) and (x2, y2)

            if math.fabs(x2 - x1) > math.fabs(y2 - y1):
                rectangle_start = (x1 + 2*x_direction, y1 + y_direction)
                rectangle_end = (x2 - 2*x_direction, y2 - y_direction)
            else:
                rectangle_start = (x1 + x_direction, y1 + 2*y_direction)
                rectangle_end = (x2 - x_direction, y2 - 2*y_direction)

            x_direction = 1
            if (corner2[0]) < (corner1[0]): x_direction = -1
            y_direction = 1
            if (corner2[1]) < (corner1[1]): y_direction = -1

            if args.debug:
                print("\trect_start " +str(rectangle_start))
                print("\trect_end " +str(rectangle_end))

            for x in range(rectangle_start[0], rectangle_end[0] + x_direction, x_direction):
                for y in range(rectangle_start[1], rectangle_end[1] + y_direction, y_direction):
                    node = (x, y)
                    if args.debug:
                        print("\tcheck " + str(node))
                    if not (node in nodes_to_check): nodes_to_check.append(node)

            for node in nodes_to_check:
                if map[node[1]][node[0]]:
                    if args.debug:
                        print("\tobstacle: " + str(node))
                    part_obstacles += 1
        
        if args.debug:
            print("\tfull obstacles: " + str(full_obstacles) + ", partial obstacles: " + str(part_obstacles))

        if (consider_obstacles_with_distance(full_obstacles, part_obstacles, distance, args.debug) <= args.connection_distance):
            are_connected = True

        if args.debug:
            if are_connected:
                print("\tconnected!")
            else:
                print("\tnot connected")

    else:
        raise RuntimeError("Unknown connection definition!")
    
    return are_connected

def get_connectivity_graph(map, args):
    connectivity_graph = {}

    # create empty connectivity graph
    for row in range(len(map)):
        for col in range(len(map[0])):
            if map[row][col] == False:
                key = (col, row)
                connectivity_graph[key] = []
    
    # populate graph
    for key in connectivity_graph.keys():
        x = key[0]
        y = key[1]
        for row in range(len(map)):
            for col in range(len(map[0])):
                if ((x, y) != (col, row)) and (map[row][col] == False):
                    if (are_vertexes_connected(map, x, y, col, row, args) == True):
                        connectivity_graph[key].append((col, row))

    return connectivity_graph

def import_connectivity_graph(filename):
    f = Path(filename)
    if not f.is_file():
        raise BaseException(filename + " does not exist.")
    f = open(filename, 'r')

    graph = {}

    while True:
        line = f.readline()
        if not line:
            break
        elements = line.split(">")

        key_coords = re.sub("[()]", "", elements[0].strip()).split(" ")
        key = (int(key_coords[0]), int(key_coords[1]))

        values = []
        raw_nodes = elements[1].strip().split(",")
        for i in range(len(raw_nodes)):
            node_coords = re.sub("[()]", "", raw_nodes[i]).split(" ")
            v = (int(node_coords[0]), int(node_coords[1]))
            values.append(v)
        
        graph[key] = values

    return graph

def print_connectivity_graph(connectivity_graph):
    for key in dict(connectivity_graph):
        print(str(key) + " is connected to: " + str(connectivity_graph[key]))
