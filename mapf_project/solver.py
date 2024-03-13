import argparse
import glob
import multiprocessing
import time
import sys
import os
from libraries.cbs import CBSSolver
from libraries.connectivity_graphs import generate_connectivity_graph, import_connectivity_graph, print_connectivity_graph, find_all_cliques
from libraries.enums import ConnectionCriterion, GoalsChoice, GoalsAssignment
from libraries.goals_choice import print_goal_positions, generate_goal_positions
from libraries.goals_assignment import print_goals_assignment, search_goals_assignment_local_search, search_goals_assignment_hungarian, get_random_goal_assignment
from libraries.utils import print_mapf_instance, import_mapf_instance, get_cbs_cost
from libraries.visualize import Enhanced_Animation

'''
    'map' and other data structures/functions associated with external libraries use (row, col) to identify nodes,
    while 'connectivity graph' and other data structures/functions in my code use (x, y),
    therefore, when passing arguments to the former, the coordinates must be switched (row = y, col = x)
'''

TIMEOUT = 60

def get_goal_positions(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]], args: list) -> list[tuple[int, int]]:
    goal_positions = []

    # a clique of nodes is generated using the requested algorithm
    start_time = time.time()
    if args.goals_choice == GoalsChoice.UNINFORMED_GENERATION.name:
        goal_positions = generate_goal_positions(starts, connectivity_graph, informed=False)
    elif args.goals_choice == GoalsChoice.INFORMED_GENERATION.name:
        goal_positions = generate_goal_positions(starts, connectivity_graph, informed=True)
    else:
        raise(RuntimeError("Unknown goals choice algorithm."))
    search_time = time.time() - start_time

    if len(goal_positions) < len(starts):
        raise(RuntimeError("This map doesn't have enough connected nodes for all its agents!"))
    
    if (args.verbose == False):
        print("Goals generation time (s):    {:.2f}\n".format(search_time))
        return goal_positions
    
    # if verbose mode is on, additional info will be produced:

    # total number of cliques of length k present in the problem instance, with k = number of agents
    cliques = find_all_cliques(connectivity_graph, len(starts))
    print("Cliques found: " + str(len(cliques)) + "\n")

    # cost of each possible solution, characterized by one clique and the best agent-goal assignment for that clique
    # the cost is found resolving each solution of the instance with CBS
    cliques_cbs_costs = []
    real_cost = multiprocessing.Value('i', 0)
    i = 0
    print("clique : lower bound (A*), real cost (CBS)")
    for clique in cliques:
        i += 1
        goal_positions_temp = []
        for n in clique:
            goal_positions_temp.append((n[1], n[0]))
        goal_assignment_temp, clique_heuristic_cost = search_goals_assignment_hungarian(map, starts, goal_positions_temp)
        
        p = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goal_assignment_temp, real_cost))
        p.start()
        counter = 0
        while (counter < TIMEOUT):
            time.sleep(1)
            counter += 1
            if (not p.is_alive()):
                break
        if (p.is_alive()):
            # if CBS fails to found paths within the time limit, a lower bound is considered
            # (sum of costs of single-agent plans found with A*, without considering conflicts, using optimal assignment found with Hungarian algorithm) 
            print("clique " + str(i) + "/" + str(len(cliques)) + " -> " + str(clique) + ": " + str(clique_heuristic_cost))
            cliques_cbs_costs.append((clique, clique_heuristic_cost))
            p.terminate()
        else:
            print("clique " + str(i) + "/" + str(len(cliques)) + " -> " + str(clique) + ": " + str(clique_heuristic_cost) + ", " + str(real_cost.value))
            cliques_cbs_costs.append((clique, real_cost.value))
        p.join()
        real_cost.value = 0
    print()

    cliques_cbs_costs.sort(key=lambda el: el[1])

    # the best and worst (in terms of cost) cliques are found
    best_clique = cliques_cbs_costs[0]
    worst_clique = cliques_cbs_costs[-1]

    # time needed to generate the goals clique with uninformed generation
    start_time = time.time()
    goal_positions_uninformed = generate_goal_positions(starts, connectivity_graph, informed=False)
    search_time = time.time() - start_time
    print("Goals positions (uninformed clique generation) search time (s):    {:.2f}\n".format(search_time))

    # time needed to generate the goals clique with informed generation
    start_time = time.time()
    goal_positions_informed = generate_goal_positions(starts, connectivity_graph, informed=True)
    search_time = time.time() - start_time
    print("Goals positions (informed clique generation) search time (s):    {:.2f}\n".format(search_time))

    # the cliques just found are in the (row, col) format, they must be converted to (x, y) format to be compared to those found earlier
    goal_positions_uninformed_clique = []
    for n in goal_positions_uninformed:
        goal_positions_uninformed_clique.append((n[1], n[0]))
    goal_positions_uninformed_clique.sort()
    print("Uninformed generation clique: " + str(goal_positions_uninformed_clique))
    goal_positions_uninformed_cost = 0

    goal_positions_informed_clique = []
    for n in goal_positions_informed:
        goal_positions_informed_clique.append((n[1], n[0]))
    goal_positions_informed_clique.sort()
    print("Informed generation clique: " + str(goal_positions_informed_clique))
    goal_positions_informed_cost = 0
    print()

    # all cliques are ranked by cost, highlighting the best one and those found with informed and uninformed generation
    for el in cliques_cbs_costs:
        label = ""
        if el == best_clique: label = " BEST"
        if el[0] == goal_positions_uninformed_clique:
            label += " uninformed gen clique"
            goal_positions_uninformed_cost = el[1]
        if el[0] == goal_positions_informed_clique:
            label += " informed gen clique"
            goal_positions_informed_cost = el[1]
        print(str(el) + label)
    print()

    # optimality of the clique found with uninformed generation
    if worst_clique[1] - best_clique[1] == 0:
        uninformed_opt_factor = 1.0
    else:
        uninformed_opt_factor = round(1 - ((goal_positions_uninformed_cost - best_clique[1]) / (worst_clique[1] - best_clique[1])), 2)
    print("Uninformed clique generation optimality: " + str(uninformed_opt_factor) + "\n")

    # optimality of the clique found with informed generation
    if worst_clique[1] - best_clique[1] == 0:
        informed_opt_factor = 1.0
    else:
        informed_opt_factor = round(1 - ((goal_positions_informed_cost - best_clique[1]) / (worst_clique[1] - best_clique[1])), 2)
    print("Informed clique generation optimality: " + str(informed_opt_factor) + "\n")

    return goal_positions

def get_goals_assignment(map: list[list[bool]], starts: list[tuple[int, int]], goal_positions: list[tuple[int, int]], args: list) -> list[tuple[int, int]]:
    goals = []

    # an agent-goal assignment is generated using the requested algorithm
    start_time = time.time()
    if args.goals_assignment == GoalsAssignment.HUNGARIAN.name:
        goals, cost = search_goals_assignment_hungarian(map, starts, goal_positions)
        algorithm_label = "Hungarian algorithm"
    elif args.goals_assignment == GoalsAssignment.LOCAL_SEARCH.name:
        goals, cost = search_goals_assignment_local_search(map, starts, goal_positions)
        algorithm_label = "Local search"
    elif args.goals_assignment == GoalsAssignment.RANDOM.name:
        goals, cost = get_random_goal_assignment(map, starts, goal_positions)
        algorithm_label = "Random"
    else:
        raise(RuntimeError("Unknown goals assignment algorithm."))
    search_time = time.time() - start_time

    if (args.verbose == False):
        return goals
    
    # if verbose mode is on, additional info will be produced:

    # time needed to generate the assignment + cost of the solution with said assignment, calculated using an heuristic (A* path lenght between agents and goals)
    print(algorithm_label + " heuristic cost: " + str(cost))
    print(algorithm_label + " time (s):    {:.2f}".format(search_time))

    # real cost of the solution with said assignment, calculated using CBS
    real_cost = multiprocessing.Value('i', 0)

    p1 = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goals, real_cost))
    p1.start()
    counter = 0
    while (counter < TIMEOUT):
        time.sleep(1)
        counter += 1
        if (not p1.is_alive()):
            break
    if (p1.is_alive()):
        print(algorithm_label + " CBS cost: not found")
        p1.terminate()
    else:
        print(algorithm_label + " CBS cost: " + str(real_cost.value))
    p1.join()

    # cost of the solution with a random assignment, calculated using an heuristic (A* path lenght between agents and goals)
    random_goals, random_cost = get_random_goal_assignment(map, starts, goal_positions)
    print("Random assignment heuristic cost: " + str(random_cost))

    # real cost of the solution with said random assignment, calculated using CBS
    random_real_cost = multiprocessing.Value('i', 0)

    p2 = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, random_goals, random_real_cost))
    p2.start()
    counter = 0
    while (counter < TIMEOUT):
        time.sleep(1)
        counter += 1
        if (not p2.is_alive()):
            break
    if (p2.is_alive()):
        print("Random assignment CBS cost: not found")
        p2.terminate()
    else:
        print("Random assignment CBS cost: " + str(random_real_cost.value))
    p2.join()
    print()

    return goals

def solve_instance(file: str, args: list) -> None:
    file_name_sections = file.split("\\")
    file_id = file_name_sections[-1].split(".")[0]
    path = "./outputs/" + file_id + ".txt"
    if (args.save_output):
        print("Solving " + file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        f = open(path, 'w')
        sys.stdout = f
        sys.stderr = f

    print("*** Import an instance ***\n")
    print("Instance: " + file + "\n")
    print("Goals choice: " + args.goals_choice)
    print("Goals assignment: " + args.goals_assignment + "\n")
    map, starts, _ = import_mapf_instance(file)
    print_mapf_instance(map, starts)

    if (args.connectivity_graph):
        print("*** Generate connectivity graph ***\n")
        connectivity_graph = generate_connectivity_graph(map, args)
        print_connectivity_graph(connectivity_graph)
    else:
        print("*** Import connectivity graph from file ***\n")
        cg_path = "./connectivity_graphs/" + file_id + ".txt"
        connectivity_graph = import_connectivity_graph(cg_path)
    print()

    print("*** Find goal positions ***\n")
    goal_positions = get_goal_positions(map, starts, connectivity_graph, args)
    print_goal_positions(goal_positions)
    print()

    print("*** Assign each agent to a goal ***\n")
    goals = get_goals_assignment(map, starts, goal_positions, args)
    print_goals_assignment(goals)
    print()

    print("*** Problem ready to be solved ***\n")
    print_mapf_instance(map, starts, goals)

    if (args.solve):
        print("***Run CBS***")
        cbs = CBSSolver(map, starts, goals)
        paths = cbs.find_solution(False)
        print()
        
        animation = Enhanced_Animation(map, starts, goals, connectivity_graph, paths)
        animation.show()
    
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve a MAPF agent meeting problem')
    parser.add_argument('--instance', type=str, default=None, required=True,
                        help='The name of the instance file(s)')
    parser.add_argument('--goals_choice', type=str, default=GoalsChoice.INFORMED_GENERATION.name, choices=[GoalsChoice.UNINFORMED_GENERATION.name, GoalsChoice.INFORMED_GENERATION.name],
                        help='The algorithm to use to select the goal nodes, defaults to ' + GoalsChoice.INFORMED_GENERATION.name)
    parser.add_argument('--goals_assignment', type=str, default=GoalsAssignment.HUNGARIAN.name, choices=[GoalsAssignment.HUNGARIAN.name, GoalsAssignment.LOCAL_SEARCH.name, GoalsAssignment.RANDOM.name],
                        help='The algorithm to use to assign each goal to an agent, defaults to ' + GoalsAssignment.HUNGARIAN.name)
    parser.add_argument('--connectivity_graph', type=bool, default=False,
                        help='Decide if you want to generate a connectivity graph for the instance or use one already generated, defaults to ' + str(False))
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.PATH_LENGTH.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.PATH_LENGTH.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.PATH_LENGTH.name)
    parser.add_argument('--connection_distance', type=float, default=3,
                        help='The distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(3))
    parser.add_argument('--solve', type=bool, default=False,
                        help='Decide to solve the instance using CBS or not, defaults to ' + str(False))
    parser.add_argument('--save_output', type=bool, default=False,
                        help='Decide to save the output in txt files, defaults to ' + str(False))
    parser.add_argument('--verbose', type=bool, default=False,
                        help='Decide to print additional data regarding the problem instance and its solution, defaults to ' + str(False))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):
        solve_instance(file, args)