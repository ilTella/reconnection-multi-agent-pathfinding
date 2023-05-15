# graph -> connectivity graph

# 1)

# definition of connection between nodes:
    # 1st version:
        # A and B are always connected (graph = connectivity graph) [X]
    # 2nd version:
        # A and B are connected if (distance(A, B) < k) [X]
    # 3rd version:
        # A and B are connected if (distance(A, B) + weight(obstacles) < k) [X]
    # 4th version:
        # A and B are always connected, unless there are obstacles between them []

# create empty connectivity graph {[x, y]: [[x1, y1],[x2, y2],[x3, y3], ...], ...} [X]
# populate connectivity graph using connection definition [X]

# 2)

# choose n goal vertexes which are connected:
    # 1st version:
        # choose goals randomly [X]
    # 2nd version:
        # choose goals with minimum distance between them and start positions [X]

# how must the nodes be connected?
    # a) all nodes must be connected [X]
    # b) a node A can be connected to B, or connected to B that is connected to C []

# 3)

# assign each goal to each agent:
    # 1st version:
        # do it randomly [X]
    # 2nd version:
        # minimize start-goal distance with greedy algorithm [X]

import argparse
import glob
import math
from cbs import CBSSolver
from visualize import Animation
from run_experiments import print_mapf_instance
from run_experiments import import_mapf_instance

CONNECTION1 = "always_connected"
CONNECTION2 = "distance"
CONNECTION3 = "distance_and_obstacles"
DEFAULT_DISTANCE = 3

CONNECTION_REQUIREMENT1 = "all_agents_connected"
CONNECTION_REQUIREMENT2 = "max_one_man-in-the-middle"

GOALS_CHOICE1 = "random"
GOALS_CHOICE2 = "minimum_distance"

GOAL_ASSIGNMENT1 = "random"
GOAL_ASSIGNMENT2 = "minimize_distance"

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

    if args.connection == CONNECTION1:
        are_connected = True

    elif args.connection == CONNECTION2:
        if get_distance(x1, y1, x2, y2) <= args.distance:
            are_connected = True

    elif args.connection == CONNECTION3:
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
            secondary1_end = [x2 + x_step, y2]
            while secondary1[0] != secondary1_end[0] + x_step and secondary1[1] != secondary1_end[1] + y_step:
                if map[secondary1[1]][secondary1[0]]: part_obstacles += 1
                secondary1[0] += x_step
                secondary1[1] += y_step

            secondary2 = [x1 + x_step, y1]
            secondary2_end = [x2, y2 + y_step]
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

        if (consider_obstacles_with_distance(full_obstacles, part_obstacles, distance, args.debug) <= args.distance):
            are_connected = True

        if args.debug:
            if are_connected: print("\tconnected")
            if not are_connected: print("\tnot connected")

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

def print_connectivity_graph(connectivity_graph):
    for key in dict(connectivity_graph):
        print(str(key) + " is connected to: " + str(connectivity_graph[key]))

def get_distance_to_all_starting_points(starts, x, y):
    total = 0

    for s in starts:
        total += get_distance(x, y, s[1], s[0])

    return round(total, 2)

def get_goal_positions(map, starts, connectivity_graph, args):
    goal_positions = []

    if args.goals_choice == GOALS_CHOICE1:

        keys = []
        for k in connectivity_graph.keys():
            if len(connectivity_graph[k]) + 1 >= len(starts): keys.append(k)
        keys = sorted(keys, key=lambda key: len(connectivity_graph[key]), reverse=True)

        if args.debug:
            print_connectivity_graph(dict((k, connectivity_graph[k]) for k in keys))

        if args.connection_requirement == CONNECTION_REQUIREMENT1:
            for k in keys:
                goal_positions.append((k[1], k[0]))
                nodes = []
                for n in connectivity_graph[k]:
                    if len(connectivity_graph[n]) + 1 >= len(starts): nodes.append(n)
                nodes = sorted(nodes, key=lambda node: len(connectivity_graph[node]), reverse=True)

                for n in nodes:
                    ok = True
                    for g in goal_positions:
                        if not (n in connectivity_graph[(g[1], g[0])]):
                            ok = False
                            break
                    if ok: goal_positions.append((n[1], n[0]))
                    if len(goal_positions) >= len(starts): break
                
                if len(goal_positions) < len(starts):
                    goal_positions = []
                    continue
                else:
                    break

            if len(goal_positions) < len(starts):
                raise(RuntimeError("This map doesn't have enough connected vertexes for all its agents!"))
                
        else:
            raise(RuntimeError("I don't know what do do yet!"))
    
    elif args.goals_choice == GOALS_CHOICE2:

        keys = []
        for k in connectivity_graph.keys():
            if len(connectivity_graph[k]) + 1 >= len(starts): keys.append(k)
        keys = sorted(keys, key=lambda key: get_distance_to_all_starting_points(starts, key[1], key[0]))

        if args.debug:
            # print nodes, ordered by distance to all starting points
            print("Cumulative distance between each node and all starting points:")
            for k in keys:
                print(str(k) + ": " + str(get_distance_to_all_starting_points(starts, k[1], k[0])))
            print()
            print_connectivity_graph(dict((k, connectivity_graph[k]) for k in keys))

        if args.connection_requirement == CONNECTION_REQUIREMENT1:
            for k in keys:
                goal_positions.append((k[1], k[0]))
                nodes = []
                for n in connectivity_graph[k]:
                    if len(connectivity_graph[n]) + 1 >= len(starts): nodes.append(n)
                nodes = sorted(nodes, key=lambda node: len(connectivity_graph[node]), reverse=True)

                for n in nodes:
                    ok = True
                    for g in goal_positions:
                        if not (n in connectivity_graph[(g[1], g[0])]):
                            ok = False
                            break
                    if ok: goal_positions.append((n[1], n[0]))
                    if len(goal_positions) >= len(starts): break
                
                if len(goal_positions) < len(starts):
                    goal_positions = []
                    continue
                else:
                    break

            if len(goal_positions) < len(starts):
                raise(RuntimeError("This map doesn't have enough connected vertexes for all its agents!"))
                
        else:
            raise(RuntimeError("I don't know what do do yet!"))
    
    else:
        raise(RuntimeError("I don't know what do do yet!"))
        
    return goal_positions

def assign_goals(map, starts, goal_positions, args):
    new_goals = []

    if args.goal_assignment == GOAL_ASSIGNMENT1:
        new_goals = goal_positions
    
    elif args.goal_assignment == GOAL_ASSIGNMENT2:
        distance_matrix = []
        
        to_assign = []
        for i in range(len(map)):
            to_assign.append(i)
        
        for n in range(len(starts)):
            distance_matrix.append([])
            for g in range(len(goal_positions)):
                distance_matrix[-1].append(get_distance(starts[n][1], starts[n][0], goal_positions[g][1], goal_positions[g][0]))
        
        if args.debug:
            # print distance_matrix
            s = "distance to:" + " "*5
            for g in range(len(goal_positions)):
                s += str((goal_positions[g][1], goal_positions[g][0])) + " "*5
            print(s + "\n")
            for r in range(len(distance_matrix)):
                s = "node" + str(r) + str((starts[r][1], starts[r][0])) + ": " + " "*5
                for c in range(len(distance_matrix[0])):
                    s += ("%.2f" % distance_matrix[r][c]) + " "*7
                print(s + "\n")
        
        # approccio greedy
        for n in range(len(starts)):
            min = 100000
            to_remove = -1
            for g in range(len(goal_positions)):
                if distance_matrix[n][g] < min and g in to_assign:
                    min = distance_matrix[n][g]
                    to_remove = g
            new_goals.append(goal_positions[to_remove])
            to_assign.remove(to_remove)

    else:
        raise(RuntimeError("I don't know what do do yet!"))

    return new_goals

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get a modified input for MAPF solver')
    parser.add_argument('--instance', type=str, default=None, help='The name of the instance file(s)')
    parser.add_argument('--connection', type=str, default=CONNECTION1, help='The connection definition to use to build the connectivity graph (one of: {always_connected,distance,distance_and_obstacles}), defaults to ' + str(CONNECTION1))
    parser.add_argument('--distance', type=float, default=DEFAULT_DISTANCE, help='The distance between vertexes used to define a connection, when using certain connection definitions, defaults to ' + str(DEFAULT_DISTANCE))
    parser.add_argument('--connection_requirement', type=str, default=CONNECTION_REQUIREMENT1, help='The requirement agents have at their goal vertexes on their connection (one of: {all_agents_connected,max_one_man-in-the-middle}), defaults to '+ str(CONNECTION_REQUIREMENT1))
    parser.add_argument('--goals_choice', type=str, default=GOALS_CHOICE1, help='The criteria to use to choose the goals (one of: {random,minimum_distance}), defaults to ' + str(GOALS_CHOICE1))
    parser.add_argument('--goal_assignment', type=str, default=GOAL_ASSIGNMENT1, help='The criteria to use to assign each goal to an agent (one of: {random,minimize_distance}), defaults to ' + str(GOAL_ASSIGNMENT1))
    parser.add_argument('--resolve', type=bool, default=False, help='Decide to resolve the instance using CBS or not, defaults to ' + str(False))
    parser.add_argument('--debug', type=bool, default=False, help='Print debug information or not, defaults to ' + str(False))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):

        print("*** Import an instance ***\n")
        my_map, starts, goals = import_mapf_instance(file)
        print_mapf_instance(my_map, starts, goals)

        print("*** Generate connectivity graph ***\n")
        connectivity_graph = get_connectivity_graph(my_map, args)
        print_connectivity_graph(connectivity_graph)
        print()

        print("*** Find new goal positions ***\n")
        goal_positions = get_goal_positions(my_map, starts, connectivity_graph, args)
        print(goal_positions)
        for goal in goal_positions:
            print("x: " + str(goal[1]) + ", y: " + str(goal[0]))
        print()

        print("*** Assign each agent to a goal ***\n")
        new_goals = assign_goals(my_map, starts, goal_positions, args)
        for i in range(len(new_goals)):
            print("agent " + str(i) + " goes to: " + str(new_goals[i][1]) + ", " + str(new_goals[i][0]))
        print()

        print("*** Modified problem ***\n")
        print_mapf_instance(my_map, starts, new_goals)

        if (args.resolve):
            print("***Run CBS***")
            cbs = CBSSolver(my_map, starts, new_goals)
            paths = cbs.find_solution(False)
            animation = Animation(my_map, starts, new_goals, paths)
            animation.show()

