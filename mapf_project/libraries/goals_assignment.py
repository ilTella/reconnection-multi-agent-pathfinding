from .single_agent_planner import compute_heuristics
from .utils import get_shortest_path_length
from random import shuffle
from itertools import permutations

def search_goals_assignment_exhaustive_search_astar(map: list[list[bool]], starts: list[tuple[int, int]], goal_positions: list[tuple[int, int]]) -> list[tuple[int, int]]:
    '''
    Explores every permutation of the goals assignment so the optimal solution (considering only single agent path lengths and not collisions between them) is garanteed,
    it is however only praticable for small instances of the problem
    '''
    
    new_goals = []

    path_length_matrix = get_path_length_matrix(map, starts, goal_positions)

    assignment = []
    for i in range(len(goal_positions)):
        assignment.append(i)

    best_assignment = assignment
    best_cost = get_assignment_cost(path_length_matrix, assignment)

    for perm in permutations(assignment):
        cost = get_assignment_cost(path_length_matrix, perm)
        if cost < best_cost:
            best_assignment = perm
            best_cost = cost

    for i in best_assignment:
        new_goals.append(goal_positions[i])

    return new_goals

def search_goals_assignment_astar(map: list[list[bool]], starts: list[tuple[int, int]], goal_positions: list[tuple[int, int]]) -> list[tuple[int, int]]:
    new_goals = []

    path_length_matrix = get_path_length_matrix(map, starts, goal_positions)
    
    initial_assignment = []
    for i in range(len(goal_positions)):
        initial_assignment.append(i)
    shuffle(initial_assignment)

    cost = get_assignment_cost(path_length_matrix, initial_assignment)
    explored_assignments = {}
    explored_assignments[tuple(initial_assignment)] = cost

    chosen_assignment = initial_assignment
    candidate_assignments = [initial_assignment]

    while (len(candidate_assignments) >= 1):
        assignment = candidate_assignments.pop()

        go_on = True
        while(go_on):
            go_on = False
            for i in range(len(assignment)):
                for j in range(i + 1, len(assignment)):
                    new_assignment = swap_assigment_indexes(assignment.copy(), i, j)
                    if tuple(new_assignment) in explored_assignments:
                        continue
                    new_cost = get_assignment_cost(path_length_matrix, new_assignment)
                    explored_assignments[tuple(new_assignment)] = new_cost
                    if new_cost == cost:
                        candidate_assignments.append(new_assignment)
                    elif new_cost < cost:
                        candidate_assignments = [new_assignment]
                        chosen_assignment = new_assignment
                        cost = new_cost
                        go_on = True
                        break
                else:
                    continue
                break

    for i in chosen_assignment:
        new_goals.append(goal_positions[i])

    return new_goals

def get_path_length_matrix(map, starts, goal_positions):
    path_length_matrix = []
    for _ in range(len(starts)):
        path_length_matrix.append([])
    
    for g in range(len(goal_positions)):
        heuristics = compute_heuristics(map, goal_positions[g])
        for s in range(len(starts)):
            path_length_matrix[s].append(get_shortest_path_length(map, starts[s], goal_positions[g], heuristics))
 
    return path_length_matrix

def get_assignment_cost(path_length_matrix, assignment):
    total = 0

    i = 0
    for j in range(len(assignment)):
        total += path_length_matrix[i][assignment[j]]
        i += 1

    return total

def swap_assigment_indexes(assignment, index1, index2):
    temp = assignment[index1]
    assignment[index1] = assignment[index2]
    assignment[index2] = temp
    return assignment

def print_goals_assignment(goals: list[tuple[int, int]]) -> None:
    for i in range(len(goals)):
        print("agent " + str(i) + " goes to: " + str(goals[i][1]) + ", " + str(goals[i][0]))