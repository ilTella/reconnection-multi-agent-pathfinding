# graph -> connectivity graph

# 1)

# definition of connection between nodes:
    # 1st version:
        # A and B are always connected (graph = connectivity graph) [X]
    # 2nd version:
        # A and B are connected if (distance(A, B) < k) [X]
    # 3rd version:
        # A and B are connected if (distance(A, B) < k && obstacles_between(A, B) < j) []

# create empty connectivity graph {[x, y]: [[x1, y1],[x2, y2],[x3, y3], ...], ...} [X]
# populate connectivity graph using connection definition [X]

# 2)

# choose n goal vertexes which are connected:
    # 1st version:
        # choose goals randomly []
    # 2nd version:
        # choose goals with minimum distance between them and start positions []

# how must the nodes be connected?
    # a) all nodes must be connected []
    # b) a node A can be connected to B, or connected to B that is connected to C []

# 3)

# assign each goal to each agent:
    # 1st version:
        # do it randomly []
    # 2nd version:
        # minimize mean start-goal distance []

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
DEFAULT_DISTANCE = 2

CONNECTION_REQUIREMENT1 = "all_agents_connected"
CONNECTION_REQUIREMENT2 = "max_one_man-in-the-middle"

GOALS_CHOICE1 = "random"
GOALS_CHOICE2 = "minimum_distance"

GOAL_ASSIGNMENT1 = "random"
GOAL_ASSIGNMENT2 = "minimize_start-goal_distance"

def are_vertexes_connected(map, x1, y1, x2, y2, connection_definition, distance_used):
    are_connected = False

    if connection_definition == CONNECTION1:
        are_connected = True
    elif connection_definition == CONNECTION2:
        if (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)) <= distance_used:
            are_connected = True
    elif connection_definition == CONNECTION3:
        are_connected = False
    else:
        raise RuntimeError("Unknown connection definition!")
    
    return are_connected

def get_connectivity_graph(map, args):
    connectivity_graph = {}

    # create empty connectivity graph
    for r in range(len(map)):
        for c in range(len(map[0])):
            if map[r][c] == False:
                key = (r, c)
                connectivity_graph[key] = []
    
    # populate graph
    for key in connectivity_graph.keys():
        x = key[0]
        y = key[1]
        for r in range(len(map)):
            for c in range(len(map[0])):
                if (x != r or y != c) and (map[r][c] == False) and are_vertexes_connected(map, x, y, r, c, args.connection, args.distance):
                    connectivity_graph[key].append((r, c))

    return connectivity_graph

def print_connectivity_graph(connectivity_graph):
    for key in dict(connectivity_graph):
        print(str(key) + " is connected to: " + str(connectivity_graph[key]))

def get_goal_positions(map, starts, connectivity_graph, args):
    goal_positions = []

    if args.goals_choice == GOALS_CHOICE1:
        starting_vertex = (-1, -1)

        keys = connectivity_graph.keys()
        keys = sorted(keys, key=lambda key: len(connectivity_graph[key]), reverse=True)

        if args.connection_requirement == CONNECTION_REQUIREMENT1:
            for k in keys:
                if len(connectivity_graph[k]) + 1 >= len(starts):
                    starting_vertex = k
                    goal_positions.append(k)
                    break
            if starting_vertex == (-1, -1):
                raise(RuntimeError("This map doesn't have enough connected vertexes for all its agents!"))
            for v in connectivity_graph[k]:
                if len(goal_positions) < len(starts):
                    goal_positions.append(v)
                else:
                    return goal_positions
        else:
            raise(RuntimeError("I don't know what do do yet!"))
        

    return goal_positions

def assign_goals(map, starts, goal_positions, args):
    new_goals = []

    if args.goal_assignment == GOAL_ASSIGNMENT1:
        new_goals = goal_positions
    else:
        raise(RuntimeError("I don't know what do do yet!"))

    return new_goals

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get a modified input for MAPF solver')
    parser.add_argument('--instance', type=str, default=None, help='The name of the instance file(s)')
    parser.add_argument('--connection', type=str, default=CONNECTION1, help='The connection definition to use to build the connectivity graph (one of: {always_connected,distance,distance_and_obstacles}), defaults to ' + str(CONNECTION1))
    parser.add_argument('--distance', type=int, default=DEFAULT_DISTANCE, help='The distance between vertexes used to define a connection, when using certain connection definitions, defaults to ' + str(DEFAULT_DISTANCE))
    parser.add_argument('--connection_requirement', type=str, default=CONNECTION_REQUIREMENT1, help='The requirement agents have at their goal vertexes on their connection (one of: {all_agents_connected,max_one_man-in-the-middle}), defaults to '+ str(CONNECTION_REQUIREMENT1))
    parser.add_argument('--goals_choice', type=str, default=GOALS_CHOICE1, help='The criteria to use to choose the goals (one of: {random,minimum_distance}), defaults to ' + str(GOALS_CHOICE1))
    parser.add_argument('--goal_assignment', type=str, default=GOAL_ASSIGNMENT1, help='The criteria to use to assign each goal to an agent (one of: {random,minimize_start-goal_distance}), defaults to ' + str(GOAL_ASSIGNMENT1))
    parser.add_argument('--resolve', type=bool, default=False, help='Decide to resolve the instance using CBS or not, defaults to ' + str(False))

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
        print()

        print("*** Assign each agent to a goal ***\n")
        new_goals = assign_goals(my_map, starts, goal_positions, args)
        print()

        print("*** Modified problem ***\n")
        print_mapf_instance(my_map, starts, new_goals)

        if (args.resolve):
            print("***Run CBS***")
            cbs = CBSSolver(my_map, starts, new_goals)
            paths = cbs.find_solution(False)
            animation = Animation(my_map, starts, new_goals, paths)
            animation.show()

