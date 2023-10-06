import argparse
import glob
import multiprocessing
import time
from random import shuffle
from typing import Optional
from connectivity_graphs import generate_connectivity_graph, get_shortest_path_length, print_connectivity_graph, import_connectivity_graph
from libraries.cbs import CBSSolver
from libraries.single_agent_planner import compute_heuristics
from libraries.visualize import Enhanced_Animation
from run_experiments import import_mapf_instance, print_locations
from libraries.enums import GoalsChoice, GoalsAssignment, ConnectionCriterion

'''
    'map' and other data structures/functions associated with external libraries use (row, col) to identify nodes,
    while 'connectivity graph' and other data structures/functions in my code use (x, y),
    therefore, when passing arguments to the former, the coordinates must be switched (row = y, col = x)
'''

SOLVER_TIMEOUT = 30

def get_distance_to_all_starting_locations(map: list[list[bool]], starts: list[tuple[int, int]], node: tuple[int, int]) -> int:
    total_distance = 0
    heuristics = compute_heuristics(map, node)

    for s in starts:
        total_distance += get_shortest_path_length(map, s, node, heuristics)

    return total_distance

def are_nodes_a_clique(nodes: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> bool:
    for n1 in nodes:
        for n2 in nodes:
            if (n1 != n2) and (not n2 in connectivity_graph[n1]):
                return False

    return True

def get_goal_positions(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]], args: list) -> list[tuple[int, int]]:
    goal_positions = []
    
    if args.goals_choice == GoalsChoice.GREEDY_MINIMIZE_DISTANCE.name:
        keys = []
        for k in connectivity_graph.keys():
            if len(connectivity_graph[k]) + 1 >= len(starts):
                keys.append(k)
        keys = sorted(keys, key=lambda key: get_distance_to_all_starting_locations(map, starts, (key[1], key[0])))
    
        for k in keys:
            candidates = [k]
            nodes = sorted(connectivity_graph[k], key=lambda node: get_distance_to_all_starting_locations(map, starts, (node[1], node[0])))
            for n in nodes:
                temp = candidates.copy()
                temp.append(n)
                if are_nodes_a_clique(temp, connectivity_graph):
                    candidates.append(n)
                if len(candidates) >= len(starts):
                    for c in candidates:
                        goal_positions.append((c[1], c[0]))
                    return goal_positions

    if len(goal_positions) < len(starts):
        raise(RuntimeError("This map doesn't have enough connected vertexes for all its agents!"))
    
    return goal_positions

def assign_goals(map: list[list[bool]], starts: list[tuple[int, int]], goal_positions: list[tuple[int, int]], args: list) -> list[tuple[int, int]]:
    new_goals = []

    if args.goals_assignment == GoalsAssignment.ARBITRARY.name:
        new_goals = goal_positions
    
    elif args.goals_assignment == GoalsAssignment.RANDOM.name:
        shuffle(goal_positions)
        new_goals = goal_positions

    elif args.goals_assignment == GoalsAssignment.GREEDY_MINIMIZE_DISTANCE.name:
        agents_to_assign = []
        for i in range(len(starts)):
            agents_to_assign.append(i)
        
        for agent in agents_to_assign:
            distances_to_goals = []
            for goal in goal_positions:
                heuristics = compute_heuristics(map, goal)
                path_length = get_shortest_path_length(map, starts[agent], goal, heuristics)
                distances_to_goals.append((goal, path_length))
            distances_to_goals = sorted(distances_to_goals, key=lambda element: element[1])
            new_goals.append(distances_to_goals[0][0])
            goal_positions.remove(distances_to_goals[0][0])

    else:
        raise(RuntimeError("I don't know what do do yet!"))

    return new_goals

def print_goal_positions(goal_positions: list[tuple[int, int]]) -> None:
    for goal in goal_positions:
        print("x: " + str(goal[1]) + ", y: " + str(goal[0]))

def print_goals_assignment(goals: list[tuple[int, int]]) -> None:
    for i in range(len(goals)):
        print("agent " + str(i) + " goes to: " + str(goals[i][1]) + ", " + str(goals[i][0]))

def print_mapf_instance(map: list[list[bool]], starts: list[tuple[int, int]], goals: Optional[list[tuple[int, int]]] = None) -> None:
    print("Start locations")
    print_locations(map, starts)
    if (goals != None):
        print("Goal locations")
        print_locations(map, goals)

def solve_instance(file, args: list) -> None:
    print("*** Import an instance ***\n")
    map, starts, _ = import_mapf_instance(file)
    print_mapf_instance(map, starts)

    if (args.connectivity_graph != None):
        print("*** Import connectivity graph from file ***\n")
        connectivity_graph = import_connectivity_graph(args.connectivity_graph)
    else:
        print("*** Generate connectivity graph ***\n")
        connectivity_graph = generate_connectivity_graph(map, args)
    print_connectivity_graph(connectivity_graph)
    print()

    print("*** Find new goal positions ***\n")
    goal_positions = get_goal_positions(map, starts, connectivity_graph, args)
    print_goal_positions(goal_positions)
    print()

    print("*** Assign each agent to a goal ***\n")
    new_goals = assign_goals(map, starts, goal_positions, args)
    print_goals_assignment(new_goals)
    print()

    print("*** Modified problem ***\n")
    print_mapf_instance(map, starts, new_goals)

    if (args.solve):
        print("***Run CBS***")
        cbs = CBSSolver(map, starts, new_goals)
        paths = cbs.find_solution(False)
        
        animation = Enhanced_Animation(map, starts, new_goals, connectivity_graph, paths)
        animation.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve a MAPF agent meeting problem')
    parser.add_argument('--instance', type=str, default=None, required=True,
                        help='The name of the instance file(s)')
    parser.add_argument('--goals_choice', type=str, default=GoalsChoice.GREEDY_MINIMIZE_DISTANCE.name, choices=[GoalsChoice.GREEDY_MINIMIZE_DISTANCE.name],
                        help='The algorithm to use to select the goal nodes, defaults to ' + GoalsChoice.GREEDY_MINIMIZE_DISTANCE.name)
    parser.add_argument('--goals_assignment', type=str, default=GoalsAssignment.GREEDY_MINIMIZE_DISTANCE.name, choices=[GoalsAssignment.ARBITRARY.name, GoalsAssignment.RANDOM.name, GoalsAssignment.GREEDY_MINIMIZE_DISTANCE.name],
                        help='The algorithm to use to assign each goal to an agent, defaults to ' + GoalsAssignment.GREEDY_MINIMIZE_DISTANCE.name)
    parser.add_argument('--connectivity_graph', type=str, default=None,
                        help='The name of the file containing the connectivity graph, if included it will be imported from said file instead of being generated')
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.PATH_LENGTH.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.PATH_LENGTH.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.PATH_LENGTH.name)
    parser.add_argument('--connection_distance', type=float, default=3,
                        help='The Euclidean distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(3))
    parser.add_argument('--solve', type=bool, default=False,
                        help='Decide to solve the instance using CBS or not, defaults to ' + str(False))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):
        p = multiprocessing.Process(target=solve_instance, name="Solve instance", args=(file, args))
        p.start()

        counter = 0
        while (counter < SOLVER_TIMEOUT):
            time.sleep(1)
            counter += 1
            if (not p.is_alive()):
                break
        if (p.is_alive()):
            print("Solver coult not finish in " + str(SOLVER_TIMEOUT) + " seconds and was terminated")
            p.terminate()
            p.join()