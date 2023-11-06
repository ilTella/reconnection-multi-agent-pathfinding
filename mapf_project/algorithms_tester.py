import argparse
import glob
import multiprocessing
import time
import sys
import math
from libraries.enums import ConnectionCriterion, GoalsChoice, GoalsAssignment
from libraries.run_experiments import import_mapf_instance
from libraries.utils import print_mapf_instance, get_cbs_cost
from libraries.connectivity_graphs import generate_connectivity_graph, import_connectivity_graph, find_all_cliques
from libraries.goals_choice import print_goal_positions, search_goal_positions_minimize_mean_distance
from libraries.goals_assignment import search_goals_assignment_exhaustive_search, search_goals_assignment_local_search

TESTER_TIMEOUT = 10

def get_goal_positions(map, starts, connectivity_graph):
    cliques = find_all_cliques(connectivity_graph, len(starts))
    print("Cliques found: " + str(len(cliques)) + "\n")

    cliques_cbs_costs = []

    real_cost = multiprocessing.Value('i', 0)
    i = 0

    print("clique | CBS cost of goal assignment found with local search")
    for clique in cliques:
        i += 1
        goal_positions_temp = []
        for n in clique:
            goal_positions_temp.append((n[1], n[0]))
        goal_assignment_temp, _ = search_goals_assignment_local_search(map, starts, goal_positions_temp)
        
        p = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goal_assignment_temp, real_cost))
        p.start()
        counter = 0
        while (counter < TESTER_TIMEOUT):
            time.sleep(1)
            counter += 1
            if (not p.is_alive()):
                break
        if (p.is_alive()):
            real_cost.value = -1
            p.terminate()
        else:
            cliques_cbs_costs.append((clique, real_cost.value))
        print("clique " + str(i) + "/" + str(len(cliques)) + " -> " + str(clique) + ": " + str(real_cost.value))
        p.join()
    print()

    cliques_cbs_costs.sort(key=lambda el: el[1])

    best_clique = cliques_cbs_costs[0]
    worst_clique = cliques_cbs_costs[-1]

    goal_positions = search_goal_positions_minimize_mean_distance(map, starts, connectivity_graph)

    goal_positions_clique = []
    for n in goal_positions:
        goal_positions_clique.append((n[1], n[0]))
    goal_positions_clique.sort()
    goal_positions_cost = 0

    for el in cliques_cbs_costs:
        label = ""
        if el == best_clique: label = " BEST"
        if el == worst_clique: label = " WORST"
        if el[0] == goal_positions_clique:
            label = " *chosen clique*"
            goal_positions_cost = el[1]
        print(str(el) + label)
    print()

    opt_factor = round(1 - ((goal_positions_cost - best_clique[1]) / (worst_clique[1] - best_clique[1])), 2)
    print("Optimality: " + str(opt_factor) + "\n")

    return goal_positions

def get_goals_assignment(map, starts, goal_positions):
    start_time = time.time()
    goals_exhaustive_search, heuristic_cost = search_goals_assignment_exhaustive_search(map, starts, goal_positions)
    print("Exhaustive search cost: " + str(heuristic_cost))
    search_time = time.time() - start_time
    print("Exhaustive search time (s):    {:.2f}".format(search_time))

    real_cost = multiprocessing.Value('i', 0)

    p = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goals_exhaustive_search, real_cost))
    p.start()
    counter = 0
    while (counter < TESTER_TIMEOUT):
        time.sleep(1)
        counter += 1
        if (not p.is_alive()):
            break
    if (p.is_alive()):
        print("Exhaustive search CBS cost: not found")
        p.terminate()
    else:
        print("Exhaustive search CBS cost: " + str(real_cost.value))
    p.join()
    

    start_time = time.time()
    goals_local_search, heuristic_cost = search_goals_assignment_local_search(map, starts, goal_positions)
    print("Local search cost: " + str(heuristic_cost))
    search_time = time.time() - start_time
    print("Local search time (s):    {:.2f}".format(search_time))

    p = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goals_local_search, real_cost))
    p.start()
    counter = 0
    while (counter < TESTER_TIMEOUT):
        time.sleep(1)
        counter += 1
        if (not p.is_alive()):
            break
    if (p.is_alive()):
        print("Local search CBS cost: not found")
        p.terminate()
    else:
        print("Local search CBS cost: " + str(real_cost.value))
    p.join()

    return goals_local_search

def solve_instance(file: str, args: list) -> None:
    if (args.save_output):
        sys.stdout = sys.__stdout__
        print("Testing " + file)
        file_name_sections = file.split("\\")
        file_id = file_name_sections[-1].split(".")[0]
        path = "./testing/" + file_id + ".txt"
        f = open(path, 'w')
        sys.stdout = f
        sys.stderr = f

    instance_start_time = time.time()

    print("Instance: " + file + "\n")
    map, starts, _ = import_mapf_instance(file)
    print_mapf_instance(map, starts)

    if (args.connectivity_graph != None):
        connectivity_graph = import_connectivity_graph(args.connectivity_graph)
    else:
        connectivity_graph = generate_connectivity_graph(map, args)

    start_time = time.time()
    goal_positions = get_goal_positions(map, starts, connectivity_graph)
    print_goal_positions(goal_positions)
    relative_time = time.time() - start_time
    print("Goal positions search time (s):    {:.2f}".format(relative_time))
    print()

    start_time = time.time()
    new_goals = get_goals_assignment(map, starts, goal_positions)
    relative_time = time.time() - start_time
    print("Goals assignment search time (s):    {:.2f}".format(relative_time))
    CPU_time = time.time() - instance_start_time
    print("Total time (s):    {:.2f}".format(CPU_time))
    print()

    print_mapf_instance(map, starts, new_goals)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test')
    parser.add_argument('--instance', type=str, default=None, required=True,
                        help='The name of the instance file(s)')
    parser.add_argument('--connectivity_graph', type=str, default=None,
                        help='The name of the file containing the connectivity graph, if included it will be imported from said file instead of being generated')
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.PATH_LENGTH.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.PATH_LENGTH.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.PATH_LENGTH.name)
    parser.add_argument('--connection_distance', type=float, default=3,
                        help='The distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(3))
    parser.add_argument('--save_output', type=bool, default=False,
                        help='Decide to save the output in txt files, defaults to ' + str(False))
    parser.add_argument('--timeout', type=bool, default=False,
                        help='Decide to terminate the solver if it cannot finish in less than a minute, defaults to ' + str(False))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):
        instance = multiprocessing.Process(target=solve_instance, name="Solve instance", args=(file, args))
        instance.start()
        instance.join()