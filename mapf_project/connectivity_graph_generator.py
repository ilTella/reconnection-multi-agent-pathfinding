import argparse
import glob
import multiprocessing
import time
import sys
from libraries.enums import ConnectionCriterion
from libraries.utils import import_mapf_instance
from libraries.connectivity_graphs import generate_connectivity_graph, save_connectivity_graph

def manage_instance(file: str, args: list) -> None:
    sys.stdout = sys.__stdout__
    print("Generating connectivity graph for " + file)
    file_name_sections = file.split("\\")
    file_id = file_name_sections[-1].split(".")[0]
    path = "./connectivity_graphs/" + file_id + ".txt"

    start_time = time.time()

    map, _, _ = import_mapf_instance(file)

    connectivity_graph = generate_connectivity_graph(map, args)

    save_connectivity_graph(connectivity_graph, path)

    CPU_time = time.time() - start_time
    print("Total time (s):    {:.2f}".format(CPU_time))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connectivity graph generator')
    parser.add_argument('--instance', type=str, default=None, required=True,
                        help='The name of the instance file(s)')
    parser.add_argument('--connection_criterion', type=str, default=ConnectionCriterion.PATH_LENGTH.name, choices=[ConnectionCriterion.NONE.name, ConnectionCriterion.DISTANCE.name, ConnectionCriterion.PATH_LENGTH.name],
                        help='The connection definition used to generate a connectivity graph, defaults to ' + ConnectionCriterion.PATH_LENGTH.name)
    parser.add_argument('--connection_distance', type=float, default=3,
                        help='The distance used to define a connection, when using connection criteria based on distance between nodes, defaults to ' + str(3))

    args = parser.parse_args()

    for file in sorted(glob.glob(args.instance)):
        instance = multiprocessing.Process(target=manage_instance, name="Solve instance", args=(file, args))
        instance.start()
        instance.join()