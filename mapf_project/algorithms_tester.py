import argparse
import glob
import multiprocessing
import time
import sys
from libraries.enums import ConnectionCriterion
from libraries.run_experiments import import_mapf_instance
from libraries.utils import print_mapf_instance, get_cbs_cost
from libraries.connectivity_graphs import generate_connectivity_graph, import_connectivity_graph, find_all_cliques, are_nodes_a_clique
from libraries.goals_choice import print_goal_positions, generate_goal_positions
from libraries.goals_assignment import search_goals_assignment_hungarian, print_goals_assignment, get_random_goal_assignment

TESTER_TIMEOUT = 15

def get_goal_positions(map, starts, connectivity_graph, args):
    if args.test_subject == "goals_choice" or args.test_subject == "both":
        cliques = find_all_cliques(connectivity_graph, len(starts))
        print("Cliques found: " + str(len(cliques)) + "\n")

        cliques_cbs_costs = []

        real_cost = multiprocessing.Value('i', 0)
        i = 0

        print("clique | CBS cost of goal assignment found with hungarian algorithm")
        for clique in cliques:
            i += 1
            goal_positions_temp = []
            for n in clique:
                goal_positions_temp.append((n[1], n[0]))
            goal_assignment_temp, _ = search_goals_assignment_hungarian(map, starts, goal_positions_temp)
            
            p = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goal_assignment_temp, real_cost))
            p.start()
            counter = 0
            while (counter < TESTER_TIMEOUT):
                time.sleep(1)
                counter += 1
                if (not p.is_alive()):
                    break
            if (p.is_alive()):
                _, real_cost.value = search_goals_assignment_hungarian(map, starts, goal_positions_temp)
                print("clique " + str(i) + "/" + str(len(cliques)) + " -> " + str(clique) + ": " + str(real_cost.value) + " (estimated)")
                p.terminate()
            else:
                print("clique " + str(i) + "/" + str(len(cliques)) + " -> " + str(clique) + ": " + str(real_cost.value))
            cliques_cbs_costs.append((clique, real_cost.value))
            p.join()
        print()

        cliques_cbs_costs.sort(key=lambda el: el[1])

        best_clique = cliques_cbs_costs[0]
        worst_clique = cliques_cbs_costs[-1]

        start_time = time.time()
        goal_positions_uninformed = generate_goal_positions(starts, connectivity_graph, informed=False)
        relative_time = time.time() - start_time
        print("Goals positions (uninformed clique generation) search time (s):    {:.2f}\n".format(relative_time))

        start_time = time.time()
        goal_positions_informed = generate_goal_positions(starts, connectivity_graph, informed=True)
        relative_time = time.time() - start_time
        print("Goals positions (informed clique generation) search time (s):    {:.2f}\n".format(relative_time))

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

        if worst_clique[1] - best_clique[1] == 0:
            uninformed_opt_factor = 1.0
        else:
            uninformed_opt_factor = round(1 - ((goal_positions_uninformed_cost - best_clique[1]) / (worst_clique[1] - best_clique[1])), 2)
        print("Uninformed clique generation optimality: " + str(uninformed_opt_factor) + "\n")

        if worst_clique[1] - best_clique[1] == 0:
            informed_opt_factor = 1.0
        else:
            informed_opt_factor = round(1 - ((goal_positions_informed_cost - best_clique[1]) / (worst_clique[1] - best_clique[1])), 2)
        print("Informed clique generation optimality: " + str(informed_opt_factor) + "\n")

        goal_positions = goal_positions_informed
    else:
        start_time = time.time()
        goal_positions = generate_goal_positions(starts, connectivity_graph, informed=True)
        relative_time = time.time() - start_time
        print("Goals positions search time (s):    {:.2f}".format(relative_time))
    return goal_positions

def get_goals_assignment(map, starts, goal_positions, args):
    if args.test_subject == "goals_assignment" or args.test_subject == "both":
        start_time = time.time()
        goals_hungarian, heuristic_cost = search_goals_assignment_hungarian(map, starts, goal_positions)
        print("Hungarian algorithm heuristic cost: " + str(heuristic_cost))
        search_time = time.time() - start_time
        print("Hungarian algorithm time (s):    {:.2f}".format(search_time))

        hungarian_real_cost = multiprocessing.Value('i', 0)

        p1 = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goals_hungarian, hungarian_real_cost))
        p1.start()
        counter = 0
        while (counter < TESTER_TIMEOUT):
            time.sleep(1)
            counter += 1
            if (not p1.is_alive()):
                break
        if (p1.is_alive()):
            print("Hungarian algorithm CBS cost: not found")
            p1.terminate()
        else:
            print("Hungarian algorithm CBS cost: " + str(hungarian_real_cost.value))
        p1.join()
        

        goals_random, heuristic_cost = get_random_goal_assignment(map, starts, goal_positions)
        print("Random assignment heuristic cost: " + str(heuristic_cost))

        random_real_cost = multiprocessing.Value('i', 0)

        p2 = multiprocessing.Process(target=get_cbs_cost, name="Get CBS cost", args=(map, starts, goals_random, random_real_cost))
        p2.start()
        counter = 0
        while (counter < TESTER_TIMEOUT):
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

        goals = goals_hungarian
    else:
        goals, _ = search_goals_assignment_hungarian(map, starts, goal_positions)

    return goals

def solve_instance(file: str, args: list) -> None:
    file_name_sections = file.split("\\")
    file_id = file_name_sections[-1].split(".")[0]
    path = "./testing/" + file_id + ".txt"
    if (args.save_output):
        sys.stdout = sys.__stdout__
        print("Testing " + file)
        f = open(path, 'w')
        sys.stdout = f
        sys.stderr = f

    print("Instance: " + file + "\n")
    map, starts, _ = import_mapf_instance(file)
    print_mapf_instance(map, starts)

    if (args.connectivity_graph):
        connectivity_graph = generate_connectivity_graph(map, args)
    else:
        cg_path = "./connectivity_graphs/" + file_id + ".txt"
        connectivity_graph = import_connectivity_graph(cg_path)

    goal_positions = get_goal_positions(map, starts, connectivity_graph, args)
    print_goal_positions(goal_positions)
    print()

    new_goals = get_goals_assignment(map, starts, goal_positions, args)
    print_goals_assignment(new_goals)
    print()

    print_mapf_instance(map, starts, new_goals)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test')
    parser.add_argument('--instance', type=str, default=None, required=True,
                        help='The name of the instance file(s)')
    parser.add_argument('--connectivity_graph', type=bool, default=False,
                        help='Decide if you want to generate a connectivity graph for the instance or use one already generated, defaults to ' + str(False))
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.PATH_LENGTH.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.PATH_LENGTH.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.PATH_LENGTH.name)
    parser.add_argument('--connection_distance', type=float, default=3,
                        help='The distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(3))
    parser.add_argument('--test_subject', type=str, default="both", choices=["goals_choice", "goals_assignment", "both"],
                        help='Algorithms to test, defaults to both goals choice and goals assignment')
    parser.add_argument('--save_output', type=bool, default=False,
                        help='Decide to save the output in txt files, defaults to ' + str(False))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):
        instance = multiprocessing.Process(target=solve_instance, name="Solve instance", args=(file, args))
        instance.start()
        instance.join()