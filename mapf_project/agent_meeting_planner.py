import argparse
import glob
import multiprocessing
import time
import sys
from libraries.cbs import CBSSolver
from libraries.connectivity_graphs import generate_connectivity_graph, import_connectivity_graph, print_connectivity_graph
from libraries.enums import ConnectionCriterion, GoalsChoice, GoalsAssignment
from libraries.goals_assignment import print_goals_assignment, search_goals_assignment_greedy, search_goals_assignment_astar, search_goals_assignment_exhaustive_search_astar, search_goals_assignment_cbs
from libraries.goals_choice import search_goal_positions_minimize_mean_distance, search_goal_positions_complete, search_goal_positions_greedy, print_goal_positions
from libraries.run_experiments import import_mapf_instance
from libraries.utils import print_mapf_instance
from libraries.visualize import Enhanced_Animation
from random import shuffle

'''
    'map' and other data structures/functions associated with external libraries use (row, col) to identify nodes,
    while 'connectivity graph' and other data structures/functions in my code use (x, y),
    therefore, when passing arguments to the former, the coordinates must be switched (row = y, col = x)
'''

SOLVER_TIMEOUT = 60

def get_goal_positions(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]], args: list) -> list[tuple[int, int]]:
    goal_positions = []
    
    if args.goals_choice == GoalsChoice.GREEDY.name:
        goal_positions = search_goal_positions_greedy(map, starts, connectivity_graph)

    if args.goals_choice == GoalsChoice.COMPLETE.name:
        goal_positions = search_goal_positions_complete(map, starts, connectivity_graph)

    if args.goals_choice == GoalsChoice.MINIMIZE_MEAN_DISTANCE.name:
        goal_positions = search_goal_positions_minimize_mean_distance(map, starts, connectivity_graph)

    if len(goal_positions) < len(starts):
        raise(RuntimeError("This map doesn't have enough connected nodes for all its agents!"))
    
    return goal_positions

def get_goals_assignment(map: list[list[bool]], starts: list[tuple[int, int]], goal_positions: list[tuple[int, int]], args: list) -> list[tuple[int, int]]:
    new_goals = []

    if args.goals_assignment == GoalsAssignment.ARBITRARY.name:
        new_goals = goal_positions
    
    elif args.goals_assignment == GoalsAssignment.RANDOM.name:
        shuffle(goal_positions)
        new_goals = goal_positions

    elif args.goals_assignment == GoalsAssignment.GREEDY.name:
        new_goals = search_goals_assignment_greedy(map, starts, goal_positions)

    elif args.goals_assignment == GoalsAssignment.EXHAUSTIVE_SEARCH_ASTAR.name:
        new_goals = search_goals_assignment_exhaustive_search_astar(map, starts, goal_positions)

    elif args.goals_assignment == GoalsAssignment.MINIMIZE_DISTANCE_ASTAR.name:
        new_goals = search_goals_assignment_astar(map, starts, goal_positions)

    elif args.goals_assignment == GoalsAssignment.MINIMIZE_DISTANCE_CBS.name:
        new_goals = search_goals_assignment_cbs(map, starts, goal_positions)

    else:
        raise(RuntimeError("Unknown goals assignment algorithm."))

    return new_goals

def solve_instance(file: str, args: list) -> None:
    if (args.save_output):
        print("Solving " + file)
        file_name_sections = file.split("\\")
        file_id = file_name_sections[-1].split(".")[0]
        path = "./outputs/" + file_id + ".txt"
        f = open(path, 'w')
        sys.stdout = f

    start_time = time.time()

    print("*** Import an instance ***\n")
    print("Instance: " + file + "\n")
    map, starts, _ = import_mapf_instance(file)
    print_mapf_instance(map, starts)

    if (args.connectivity_graph != None):
        print("*** Import connectivity graph from file ***\n")
        connectivity_graph = import_connectivity_graph(args.connectivity_graph)
    else:
        print("*** Generate connectivity graph ***\n")
        connectivity_graph = generate_connectivity_graph(map, args)
    print_connectivity_graph(connectivity_graph)
    CPU_time = time.time() - start_time
    print("CPU time (s):    {:.2f}".format(CPU_time))
    print()

    print("*** Find new goal positions ***\n")
    goal_positions = get_goal_positions(map, starts, connectivity_graph, args)
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
    parser.add_argument('--goals_choice', type=str, default=GoalsChoice.MINIMIZE_MEAN_DISTANCE.name, choices=[GoalsChoice.GREEDY.name, GoalsChoice.COMPLETE.name, GoalsChoice.MINIMIZE_MEAN_DISTANCE.name],
                        help='The algorithm to use to select the goal nodes, defaults to ' + GoalsChoice.MINIMIZE_MEAN_DISTANCE.name)
    parser.add_argument('--goals_assignment', type=str, default=GoalsAssignment.MINIMIZE_DISTANCE_ASTAR.name, choices=[GoalsAssignment.ARBITRARY.name, GoalsAssignment.RANDOM.name, GoalsAssignment.GREEDY.name, GoalsAssignment.EXHAUSTIVE_SEARCH_ASTAR.name, GoalsAssignment.MINIMIZE_DISTANCE_ASTAR.name, GoalsAssignment.MINIMIZE_DISTANCE_CBS.name],
                        help='The algorithm to use to assign each goal to an agent, defaults to ' + GoalsAssignment.MINIMIZE_DISTANCE_ASTAR.name)
    parser.add_argument('--connectivity_graph', type=str, default=None,
                        help='The name of the file containing the connectivity graph, if included it will be imported from said file instead of being generated')
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.PATH_LENGTH.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.PATH_LENGTH.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.PATH_LENGTH.name)
    parser.add_argument('--connection_distance', type=float, default=3,
                        help='The Euclidean distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(3))
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