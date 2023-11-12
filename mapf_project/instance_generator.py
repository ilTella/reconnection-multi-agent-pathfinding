import argparse
import math
import random
import sys

def generate_map(size: int, density: int) -> list[list[bool]]:
    random.seed()

    map = []
    for _ in range(size):
        map.append([])
    for el in map:
        for _ in range(size):
            el.append(False)
    
    num_of_obstacles = math.floor(size**2 * density/100)
    
    while num_of_obstacles > 0:
        x = random.randint(0, size-1)
        y = random.randint(0, size-1)
        if map[x][y] == True:
            continue

        map[x][y] = True
        num_of_obstacles -= 1
    
    return map

def generate_agents_start_positions(map: list[list[bool]], num_of_agents: int, size: int) -> list[tuple[int, int]]:
    random.seed()
    agents_positions = []

    while len(agents_positions) < num_of_agents:
        x = random.randint(0, size-1)
        y = random.randint(0, size-1)
        if map[x][y] == True:
            continue
        if (x, y) in agents_positions:
            continue
        agents_positions.append((x, y))
    
    return agents_positions

def print_instance(map: list[list[bool]], agents_positions: list[tuple[int, int]], size: int) -> None:
    for x in range(args.size):
        for y in range(args.size):
            if (x, y) in agents_positions:
                i = agents_positions.index((x, y))
                print(str(i) + " ", end='')
            elif map[x][y] == True:
                print('@ ', end='')
            else:
                print('. ', end='')
        print()

    i = 0
    print("agent i: (row, col)")
    for agent in agents_positions:
        print("agent " + str(i) + ": " + str(agent))
        i += 1

def save_output(map: list[list[bool]], agents_positions: list[tuple[int, int]], args: list, file_name: str) -> None:
    size_prefix = "s" + str(args.size) + "_"
    density_prefix = "d" + str(args.density) + "_"
    agents_prefix = "a" + str(args.agents) + "_"
    path = "./custom_instances/" + size_prefix + density_prefix + agents_prefix + file_name + ".txt"

    f = open(path, 'w')
    sys.stdout = f

    print(str(args.size) + " " + str(args.size))

    for x in range(args.size):
        for y in range(args.size):
            if map[x][y] == True:
                print('@ ', end='')
            else:
                print('. ', end='')
        print()

    print(str(args.agents))
    for agent in agents_positions:
        print(str(agent[0]) + " " + str(agent[1]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a MAPF instance')
    parser.add_argument('--size', type=int, default=8, choices=range(5, 101),
                        help='Size of the instance, defaults to 8')
    parser.add_argument('--density', type=int, default=10, choices=range(0, 40, 10),
                        help='Obstacles density, defaults to 10(%)')
    parser.add_argument('--agents', type=int, default=5, choices=range(5, 16),
                        help='Number of agents, defaults to 5')
    args = parser.parse_args()

    map = generate_map(args.size, args.density)
    agents_positions = generate_agents_start_positions(map, args.agents, args.size)
    print_instance(map, agents_positions, args.size)

    response = input("\nSave? y/n\t")
    if response == "y":
        file_name = input("File name?\t")
        save_output(map, agents_positions, args, file_name)