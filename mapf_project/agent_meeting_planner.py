import argparse
import glob
import multiprocessing
import time
from connectivity_graphs import get_connectivity_graph, print_connectivity_graph, import_connectivity_graph
from libraries.cbs import CBSSolver
from libraries.single_agent_planner import a_star, compute_heuristics
from libraries.visualize import Enhanced_Animation
from run_experiments import import_mapf_instance, print_mapf_instance
from libraries.enums import GoalsChoice, GoalsAssignment, ConnectionCriterion, ConnectionRequirement

SOLVER_TIMEOUT = 30

def get_shortest_path_length(map, start_node, goal_node, heuristics):
    path = a_star(map, start_node, goal_node, heuristics, 0, [])
    return len(path) - 1

def get_distance_to_all_starting_points(map, starts, x, y):
    total = 0
    goal = (x, y)
    heuristics = compute_heuristics(map, goal)

    for s in starts:
        total += get_shortest_path_length(map, s, goal, heuristics)

    return total

def are_goals_connected_even_indirectly(node, goal, connectivity_graph, goal_positions, debug):
    res = False

    if (goal[1], goal[0]) in connectivity_graph[node]:
        if (debug):
            print(str(node) + "connected directly to " + str((goal[1], goal[0])))
        return True
    
    for g in goal_positions:
        if (g[1], g[0]) in connectivity_graph[node]:
            if (goal[1], goal[0]) in connectivity_graph[(g[1], g[0])]:
                if (debug):
                    print(str(node) + "connected to " + str((goal[1], goal[0])) + " through " + str((g[1], g[0])))
                res = True
                break

    return res

def get_goal_positions(map, starts, connectivity_graph, args):
    goal_positions = []

    if args.goals_choice == GoalsChoice.RANDOM.name:
        keys = []
        for k in connectivity_graph.keys():
            if len(connectivity_graph[k]) + 1 >= len(starts) or args.connection_requirement != ConnectionRequirement.DIRECT.name:
                keys.append(k)
        keys = sorted(keys, key=lambda key: len(connectivity_graph[key]), reverse=True)

        if args.debug:
            print_connectivity_graph(dict((k, connectivity_graph[k]) for k in keys))
    
    elif args.goals_choice == GoalsChoice.MINIMIZE_DISTANCE.name:
        keys = []
        for k in connectivity_graph.keys():
            if len(connectivity_graph[k]) + 1 >= len(starts) or args.connection_requirement != ConnectionRequirement.DIRECT.name:
                keys.append(k)
        keys = sorted(keys, key=lambda key: get_distance_to_all_starting_points(map, starts, key[1], key[0]))

        if args.debug:
            # print nodes, ordered by distance to all starting points
            print("Cumulative distance between each node and all starting points:")
            for k in keys:
                print(str(k) + ": " + str(get_distance_to_all_starting_points(map, starts, k[1], k[0])))
            print()
            print_connectivity_graph(dict((k, connectivity_graph[k]) for k in keys))
    
    if args.connection_requirement == ConnectionRequirement.DIRECT.name:
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
                if ok:
                    goal_positions.append((n[1], n[0]))
                if len(goal_positions) >= len(starts):
                    break
            
            if len(goal_positions) < len(starts):
                goal_positions = []
                continue
            else:
                break

    if args.connection_requirement == ConnectionRequirement.INDIRECT.name: # prima versione, max 1 "agente intermediario"
        for k in keys:
            ok = True
            for g in goal_positions:
                if not are_goals_connected_even_indirectly(k, g, connectivity_graph, goal_positions, args.debug):
                    ok = False
            if ok:
                goal_positions.append((k[1], k[0]))
            else:
                continue 
            
            for n in connectivity_graph[k]:
                ok = True
                for g in goal_positions:
                    if not are_goals_connected_even_indirectly(n, g, connectivity_graph, goal_positions, args.debug):
                        ok = False
                if ok:
                    goal_positions.append((n[1], n[0]))
                if len(goal_positions) >= len(starts):
                    break
            
            if len(goal_positions) < len(starts):
                goal_positions = []
                continue
            else:
                break

    if len(goal_positions) < len(starts):
        raise(RuntimeError("This map doesn't have enough connected vertexes for all its agents!"))
    
    return goal_positions

def assign_goals(map, starts, goal_positions, args):
    new_goals = []

    if args.goals_assignment == GoalsAssignment.RANDOM.name:
        new_goals = goal_positions
    
    elif args.goals_assignment == GoalsAssignment.MINIMIZE_DISTANCE.name:
        distance_matrix = []
        
        to_assign = []
        for i in range(len(goal_positions)):
            to_assign.append(i)
        
        for n in range(len(starts)):
            distance_matrix.append([])
            for g in range(len(goal_positions)):
                heuristics = compute_heuristics(map, (goal_positions[g][1], goal_positions[g][0]))
                distance_matrix[-1].append(get_shortest_path_length(map, starts[n], goal_positions[g], heuristics))
        
        if args.debug:
            # print distance_matrix
            s = "distance to:" + " "*5
            for g in range(len(goal_positions)):
                s += str((goal_positions[g][1], goal_positions[g][0])) + " "*5
            print(s + "\n")
            for r in range(len(distance_matrix)):
                s = "node_" + str(r) + str((starts[r][1], starts[r][0])) + ": " + " "*5
                for c in range(len(distance_matrix[0])):
                    s += ("%.2f" % distance_matrix[r][c]) + " "*7
                print(s + "\n")
        
        # approccio greedy
        for n in range(len(starts)):
            min = 100000
            to_remove = -1
            for g in range(len(goal_positions)):
                if (distance_matrix[n][g] < min) and (g in to_assign):
                    min = distance_matrix[n][g]
                    to_remove = g
            new_goals.append(goal_positions[to_remove])
            to_assign.remove(to_remove)

    else:
        raise(RuntimeError("I don't know what do do yet!"))

    return new_goals

def solve_instance(file, args):
    print("*** Import an instance ***\n")
    my_map, starts, goals = import_mapf_instance(file)
    print_mapf_instance(my_map, starts, goals)

    if (args.connectivity_graph != None):
        print("*** Import connectivity graph from file ***\n")
        connectivity_graph = import_connectivity_graph(args.connectivity_graph)
    else:
        print("*** Generate connectivity graph ***\n")
        connectivity_graph = get_connectivity_graph(my_map, args)
    print_connectivity_graph(connectivity_graph)
    print()

    print("*** Find new goal positions ***\n")
    goal_positions = get_goal_positions(my_map, starts, connectivity_graph, args)
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

    if (args.solve):
        print("***Run CBS***")
        cbs = CBSSolver(my_map, starts, new_goals)
        paths = cbs.find_solution(False)
        
        animation = Enhanced_Animation(my_map, starts, new_goals, connectivity_graph, paths)
        animation.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve a MAPF agent meeting problem')
    parser.add_argument('--instance', type=str, default=None, required=True,
                        help='The name of the instance file(s)')
    parser.add_argument('--goals_choice', type=str, default=GoalsChoice.MINIMIZE_DISTANCE.name, choices=[GoalsChoice.RANDOM.name, GoalsChoice.MINIMIZE_DISTANCE.name],
                        help='The criterion to use to select the goal nodes, defaults to ' + GoalsChoice.MINIMIZE_DISTANCE.name)
    parser.add_argument('--goals_assignment', type=str, default=GoalsAssignment.MINIMIZE_DISTANCE.name, choices=[GoalsAssignment.RANDOM.name, GoalsAssignment.MINIMIZE_DISTANCE.name],
                        help='The criterion to use to assign each goal to an agent, defaults to ' + GoalsAssignment.MINIMIZE_DISTANCE.name)
    parser.add_argument('--connectivity_graph', type=str, default=None,
                        help='The name of the file containing the connectivity graph, if included it will be imported from said file instead of being generated')
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.DISTANCE_AND_OBSTACLES.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.DISTANCE_AND_OBSTACLES.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.DISTANCE_AND_OBSTACLES.name)
    parser.add_argument('--connection_requirement', type=str, default=ConnectionRequirement.DIRECT.name, choices=[ConnectionRequirement.DIRECT.name, ConnectionRequirement.INDIRECT.name],
                        help='The requirement agents have to satisfy regarding the connection between them, defaults to '+ ConnectionRequirement.DIRECT.name)
    parser.add_argument('--connection_distance', type=float, default=2,
                        help='The Euclidean distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(2))
    parser.add_argument('--solve', type=bool, default=False,
                        help='Decide to solve the instance using CBS or not, defaults to ' + str(False))
    parser.add_argument('--debug', type=bool, default=False,
                        help='Print debug information or not, defaults to ' + str(False))

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