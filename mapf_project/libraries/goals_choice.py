from .single_agent_planner import compute_heuristics
from .utils import get_shortest_path_length
from .connectivity_graphs import get_reduced_connectivity_graph, find_all_cliques, find_a_clique

def search_goal_positions_complete(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> list[tuple[int, int]]:
    goal_positions = []

    connectivity_graph = get_reduced_connectivity_graph(connectivity_graph, len(starts))

    chosen_clique = find_a_clique(connectivity_graph, connectivity_graph.keys(), len(starts))

    if chosen_clique != []:
        for node in chosen_clique:
            goal_positions.append((node[1], node[0]))

    return goal_positions

def search_goal_positions_improved_complete(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> list[tuple[int, int]]:
    goal_positions = []

    connectivity_graph = get_reduced_connectivity_graph(connectivity_graph, len(starts))

    keys_with_cost = []
    for k in connectivity_graph.keys():
        keys_with_cost.append((k, get_distance_to_all_starting_locations(map, starts, (k[1], k[0]))))
    keys_with_cost = sorted(keys_with_cost, key=lambda node: node[1])
    keys = [k[0] for k in keys_with_cost]

    chosen_clique = find_a_clique(connectivity_graph, keys, len(starts))

    if chosen_clique != []:
        for node in chosen_clique:
            goal_positions.append((node[1], node[0]))

    return goal_positions

def search_goal_positions_minimize_mean_distance(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> list[tuple[int, int]]:
    goal_positions = []

    connectivity_graph = get_reduced_connectivity_graph(connectivity_graph, len(starts))

    cliques = find_all_cliques(connectivity_graph, len(starts))

    mean_distance_table = {}
    for node in connectivity_graph.keys():
        dist = get_distance_to_all_starting_locations(map, starts, (node[1], node[0]))
        mean_distance_table[node] = dist/len(starts)

    clique_mean_distance_table = {}
    for clique in cliques:
        sum = 0
        for node in clique:
            sum += mean_distance_table[node]
        clique_mean_distance_table[tuple(clique)] = sum

    cliques = sorted(cliques, key=lambda clique: clique_mean_distance_table[tuple(clique)])

    #for c in cliques:
    #    print(str(c) + ": " + str(clique_mean_distance_table[tuple(c)]))

    for node in cliques[0]:
            goal_positions.append((node[1], node[0]))

    return goal_positions

def search_goal_positions_generate_clique(map: list[list[bool]], starts: list[tuple[int, int]], connectivity_graph: dict[tuple[int, int], list[tuple[int, int]]]) -> list[tuple[int, int]]:
    goal_positions = []

    connectivity_graph = get_reduced_connectivity_graph(connectivity_graph, len(starts))

    keys_with_cost = []
    for k in connectivity_graph.keys():
        keys_with_cost.append((k, get_distance_to_all_starting_locations(map, starts, (k[1], k[0]))))
    keys_with_cost = sorted(keys_with_cost, key=lambda node: node[1])
    keys = [k[0] for k in keys_with_cost]

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
        clique_lists[level].remove(clique_lists[level][0])

        intersection = connectivity_graph[current_clique[0]].copy()
        for i in range(1, len(current_clique)-1):
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

        level += 1

    if len(clique_lists[-1]) > 0:
        chosen_clique = clique_lists[-1][0]

    if chosen_clique != []:
        for node in chosen_clique:
            goal_positions.append((node[1], node[0]))

    return goal_positions

def get_distance_to_all_starting_locations(map: list[list[bool]], starts: list[tuple[int, int]], node: tuple[int, int]) -> int:
    total_distance = 0
    heuristics = compute_heuristics(map, node)

    for s in starts:
        total_distance += get_shortest_path_length(map, s, node, heuristics)

    return total_distance

def print_goal_positions(goal_positions: list[tuple[int, int]]) -> None:
    for goal in goal_positions:
        print("x: " + str(goal[1]) + ", y: " + str(goal[0]))