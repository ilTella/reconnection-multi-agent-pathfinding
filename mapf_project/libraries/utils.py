import math
import multiprocessing
from .single_agent_planner import a_star, get_sum_of_cost
from .run_experiments import print_locations
from .cbs import CBSSolver
from typing import Optional

def get_euclidean_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2)), 2)

def get_shortest_path_length(map: list[list[bool]], start_node: tuple[int, int], goal_node: tuple[int, int], heuristics: dict) -> int:
    path = a_star(map, start_node, goal_node, heuristics, 0, [])
    return len(path) - 1

def print_mapf_instance(map: list[list[bool]], starts: list[tuple[int, int]], goals: Optional[list[tuple[int, int]]] = None) -> None:
    print("Start locations")
    print_locations(map, starts)
    if (goals != None):
        print("Goal locations")
        print_locations(map, goals)

def get_cbs_cost(map: list[list[bool]], starts: list[tuple[int, int]], goals: list[tuple[int, int]], shared_var):
    cbs = CBSSolver(map, starts, goals, doPrint=False)
    paths = cbs.find_solution(disjoint=False)
    cost = get_sum_of_cost(paths, goals, starts)
    shared_var.value = cost