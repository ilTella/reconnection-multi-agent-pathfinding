from .single_agent_planner import compute_heuristics
from .utils import get_shortest_path_length

def get_distance_to_all_starting_locations(map: list[list[bool]], starts: list[tuple[int, int]], node: tuple[int, int]) -> int:
    total_distance = 0
    heuristics = compute_heuristics(map, node)

    for s in starts:
        total_distance += get_shortest_path_length(map, s, node, heuristics)

    return total_distance

def print_goal_positions(goal_positions: list[tuple[int, int]]) -> None:
    for goal in goal_positions:
        print("x: " + str(goal[1]) + ", y: " + str(goal[0]))