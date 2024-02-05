# Reconnection Multi-Agent Pathfinding (R-MAPF)

This repository contains a framework for studying the R-MAPF problem, which is a generalization of MAM (Multi-Agent Meeting) where a set of strongly connected nodes must be found, for multiple agents to meet.
To solve a R-MAPF instance, first a set of goal nodes is generated, then an agent-goal assignment is determined and, lastly, paths are generated using CBS (Conflict-Based Search).

## How to use

While inside the main directory, run `solver.py` to solve instances of the problem.

* `python solver.py --instance .\custom_instances\s8_d10_a8_test_1.txt` generates a set of goals and determines agent-goal assignment for the requested istance

* `python solver.py --instance .\custom_instances\s8_d10_a8_test_1.txt --solve True` solves completely the requested istance, generates optimal paths and creates a visualization of the paths' execution

There are several options available, run `python solver.py --help` for a complete list.

If `--save_output` flag is set true, solutions will be saved in text files, inside this directory: `.\outputs\`.

## Code organization

Instances are saved as `.txt` files inside `.\custom_instances\`. Instances inside `.\instances` are taken from <a src="https://github.com/SvetaLadigin/robotics_mini_project">here</a>.

Inside `.\connectivity_graphs\` there are the connectivity graphs associated with the problem instances. To be properly loaded by the solver, they must have the same name as the instance they refer to.

`.\libraries\` contains code used to run the solver. `goals_choice.py` contains functions used to generate the set of goals; `goals_assignment.py` contains functions used to determine the agent-goal assignment.
`cbs.py`, `single_agent_planner.py` and `visualize.py` are imported, without any modifying (except in a single marked occasion) from <a src="https://github.com/SvetaLadigin/robotics_mini_project">this repository</a>.

You can run `data_aggregator.py` to collect data from solved instances logs in `.\outputs\` and create charts. `.\charts\` contains charts made in this way.

With `instance_generator.py` you can create new instances. It is not garanteed for generated instances to be legal, you must check for unconnected nodes in the graph, which will cause errors. Be sure to create a connectivity graph for each newly created instance, using `connectivity_graph_generator.py`.