# graph -> connectivity graph

# 1)

# definition of connection between nodes:
    # 1st version:
        # A and B are always connected (graph = connectivity graph)
    # 2nd version:
        # A and B are connected if (distance(A, B) < k)
    # 3rd version:
        # A and B are connected if (distance(A, B) < k && obstacles_between(A, B) < j)

# create empty connectivity graph {[x, y]: [[x1, y1],[x2, y2],[x3, y3], ...], ...}
# populate connectivity graph using connection definition

# 2)

# choose n goal vertexes which are connected:
    # 1st version:
        # choose goals randomly
    # 2nd version:
        # choose goals with minimum distance between them and start positions 

# 3)

# assign each goal to each agent:
    # 1st version:
        # do it randomly
    # 2nd version:
        # minimize mean start-goal distance

import argparse
import glob
from run_experiments import print_mapf_instance
from run_experiments import import_mapf_instance

CONNECTION1 = "always_connected"
CONNECTION2 = "distance"
CONNECTION3 = "distance_and_obstacles"

GOALS_CHOICE1 = "random"
GOALS_CHOICE2 = "minimum_distance"

GOAL_ASSIGNMENT1 = "random"
GOAL_ASSIGNMENT2 = "minimize_start-goal_distance"

def are_vertexes_connected(map, x1, y1, x2, y2, connection_definition):
    are_connected = False

    if connection_definition == CONNECTION1:
        are_connected = True
    elif connection_definition == CONNECTION2:
        are_connected = False
    elif connection_definition == CONNECTION3:
        are_connected = False
    else:
        raise RuntimeError("Unknown connection definition!")
    
    return are_connected

def get_connectivity_graph(map,  connection_definition):
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
                if (x != r or y != c) and (map[r][c] == False) and are_vertexes_connected(map, x, y, r, c, connection_definition):
                    connectivity_graph[key].append((r, c))

    return connectivity_graph

def print_connectivity_graph(connectivity_graph):
    for key in dict(connectivity_graph):
        print(str(key) + " is connected to: " + str(connectivity_graph[key]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get a modified input for MAPF solver')
    parser.add_argument('--instance', type=str, default=None, help='The name of the instance file(s)')
    parser.add_argument('--connection', type=str, default=CONNECTION1, help='The connection definition to use to build the connectivity graph (one of: {always_connected,distance,distance_and_obstacles}), defaults to ' + str(CONNECTION1))
    parser.add_argument('--goals-choice', type=str, default=GOALS_CHOICE1, help='The criteria to use to choose the goals (one of: {random,minimum_distance}), defaults to ' + str(GOALS_CHOICE1))
    parser.add_argument('--goal-assignment', type=str, default=GOAL_ASSIGNMENT1, help='The criteria to use to assign each goal to an agent (one of: {random,minimize_start-goal_distance}), defaults to ' + str(GOAL_ASSIGNMENT1))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):

        print("***Import an instance***\n")
        my_map, starts, goals = import_mapf_instance(file)
        print_mapf_instance(my_map, starts, goals)

        print("***Generate connectivity graph***\n")
        connectivity_graph = get_connectivity_graph(my_map, args.connection)
        print_connectivity_graph(connectivity_graph)

