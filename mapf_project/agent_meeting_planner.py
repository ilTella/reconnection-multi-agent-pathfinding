import argparse
import glob
import multiprocessing
import time
import sys
from libraries.cbs import CBSSolver
from libraries.connectivity_graphs import generate_connectivity_graph, import_connectivity_graph, print_connectivity_graph
from libraries.enums import ConnectionCriterion, GoalsChoice, GoalsAssignment
from libraries.goals_choice import print_goal_positions, generate_goal_positions
from libraries.goals_assignment import print_goals_assignment, search_goals_assignment_local_search, search_goals_assignment_hungarian
from libraries.utils import print_mapf_instance, import_mapf_instance
from libraries.visualize import Enhanced_Animation

'''
    'map' and other data structures/functions associated with external libraries use (row, col) to identify nodes,
    while 'connectivity graph' and other data structures/functions in my code use (x, y),
    therefore, when passing arguments to the former, the coordinates must be switched (row = y, col = x)
'''

SOLVER_TIMEOUT = 60

def get_goal_positions(starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]], args: list) -> list[tuple[int, int]]:
    goal_positions = []

    if args.goals_choice == GoalsChoice.UNINFORMED_GENERATION.name:
        goal_positions = generate_goal_positions(starts, connectivity_graph, informed=False)

    elif args.goals_choice == GoalsChoice.INFORMED_GENERATION.name:
        goal_positions = generate_goal_positions(starts, connectivity_graph, informed=True)

    else:
        raise(RuntimeError("Unknown goals choice algorithm."))

    if len(goal_positions) < len(starts):
        raise(RuntimeError("This map doesn't have enough connected nodes for all its agents!"))
    
    return goal_positions

def get_goals_assignment(map: list[list[bool]], starts: list[tuple[int, int]], goal_positions: list[tuple[int, int]], args: list) -> list[tuple[int, int]]:
    new_goals = []

    if args.goals_assignment == GoalsAssignment.HUNGARIAN.name:
        new_goals, _ = search_goals_assignment_hungarian(map, starts, goal_positions)

    elif args.goals_assignment == GoalsAssignment.LOCAL_SEARCH.name:
        new_goals, _ = search_goals_assignment_local_search(map, starts, goal_positions)

    else:
        raise(RuntimeError("Unknown goals assignment algorithm."))

    return new_goals

def solve_instance(file: str, args: list) -> None:
    file_name_sections = file.split("\\")
    file_id = file_name_sections[-1].split(".")[0]
    path = "./outputs/" + file_id + ".txt"
    if (args.save_output):
        print("Solving " + file)
        f = open(path, 'w')
        sys.stdout = f
        sys.stderr = f

    start_time = time.time()

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
    CPU_time = time.time() - start_time
    print("CPU time (s):    {:.2f}".format(CPU_time))
    print()

    print("*** Find new goal positions ***\n")
    goal_positions = get_goal_positions(starts, connectivity_graph, args)
    print_goal_positions(goal_positions)
    CPU_time = time.time() - start_time
    print("CPU time (s):    {:.2f}".format(CPU_time))
    print()

    print("*** Assign each agent to a goal ***\n")
    new_goals = get_goals_assignment(map, starts, goal_positions, args)
    print_goals_assignment(new_goals)
    CPU_time = time.time() - start_time
    print("CPU time (s):    {:.2f}".format(CPU_time))
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
    parser.add_argument('--goals_choice', type=str, default=GoalsChoice.INFORMED_GENERATION.name, choices=[GoalsChoice.UNINFORMED_GENERATION.name, GoalsChoice.INFORMED_GENERATION.name],
                        help='The algorithm to use to select the goal nodes, defaults to ' + GoalsChoice.INFORMED_GENERATION.name)
    parser.add_argument('--goals_assignment', type=str, default=GoalsAssignment.HUNGARIAN.name, choices=[GoalsAssignment.HUNGARIAN.name, GoalsAssignment.LOCAL_SEARCH.name],
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
    parser.add_argument('--timeout', type=bool, default=False,
                        help='Decide to terminate the solver if it cannot finish in less than a minute, defaults to ' + str(False))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):
        p = multiprocessing.Process(target=solve_instance, name="Solve instance", args=(file, args))
        p.start()

        if (args.timeout):
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