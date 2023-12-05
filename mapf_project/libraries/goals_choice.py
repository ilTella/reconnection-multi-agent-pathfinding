from .utils import get_euclidean_distance
from .connectivity_graphs import get_reduced_connectivity_graph, are_nodes_a_clique

def generate_goal_positions(starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]], informed: bool) -> list[tuple[int, int]]:
    goal_positions = []

    connectivity_graph = get_reduced_connectivity_graph(connectivity_graph, len(starts))

    keys = list(connectivity_graph.keys())
    if (informed):
        distance_matrix = get_distance_matrix(starts, keys)

        keys_with_cost = {}
        for k in range(len(keys)):
            distance_to_all_starting_locations = 0
            for s in range(len(starts)):
                distance_to_all_starting_locations += distance_matrix[s][k]
            keys_with_cost[keys[k]] = distance_to_all_starting_locations

        keys = sorted(keys, key=lambda node: keys_with_cost[node])

    chosen_clique = []
    clique_lists = []
    for _ in range(len(starts)):
        clique_lists.append([])
    for k in keys:
        clique_lists[0].append([k])

    level = 0
    while clique_lists[-1] == []:
        if level < 0:
            break
        if clique_lists[level] == []:
            level -= 1
            continue
        
        current_clique = clique_lists[level][0]
        clique_lists[level].remove(current_clique)

        intersection = connectivity_graph[current_clique[0]].copy()
        for i in range(1, len(current_clique)):
            intersection = list(set(intersection) & set(connectivity_graph[current_clique[i]]))

        nodes_to_add = intersection.copy()
        new_cliques_added = 0
        for node in nodes_to_add:
            if node not in current_clique:
                new_clique = current_clique.copy()
                new_clique.append(node)
                clique_lists[level+1].append(new_clique)
                new_cliques_added += 1
        if new_cliques_added == 0:
            continue
        else:
            level += 1
            if (informed):
                clique_lists[level] = sorted(clique_lists[level], key=lambda clique: get_max_cost(clique, keys_with_cost))

    if len(clique_lists[-1]) > 0:
        chosen_clique = clique_lists[-1][0]

    if chosen_clique != []:
        for node in chosen_clique:
            goal_positions.append((node[1], node[0]))

    return goal_positions

def get_max_cost(clique, keys_costs):
    max = 0
    for node in clique:
        if keys_costs[node] > max:
            max = keys_costs[node]
    return max

def get_distance_matrix(starts: list[tuple[int, int]], nodes: list[tuple[int, int]]) -> list[list[int]]:
    matrix = []
    for _ in range(len(starts)):
        matrix.append([])

    for i in range(len(matrix)):
        for node in nodes:
            matrix[i].append(get_euclidean_distance(starts[i][0], starts[i][1], node[1], node[0]))

    return matrix

def print_goal_positions(goal_positions: list[tuple[int, int]]) -> None:
    for goal in goal_positions:
        print("x: " + str(goal[1]) + ", y: " + str(goal[0]))