import os
import sys
import matplotlib.pyplot as plt
import numpy as np

def aggregate_data() -> None:
    number_of_cliques = []

    uninformed_optimality_values = []
    uninformed_times = []
    informed_optimality_values = []
    informed_times = []

    hungarian_heuristic_values = []
    hungarian_cbs_values = []
    hungarian_times = []
    random_heuristic_values = []
    random_cbs_values = []

    for filename in os.listdir("./testing/"):
        path = "./testing/" + filename
        with open(path, 'r') as f:
            while True:
                line = f.readline()
                if line == "":
                    break
                if "Cliques found" in line:
                    elements = line.split(": ")
                    number_of_cliques.append(int(elements[1].strip()))
                if "Uninformed clique generation optimality" in line:
                    elements = line.split(": ")
                    uninformed_optimality_values.append(float(elements[1].strip()))
                if "Informed clique generation optimality" in line:
                    elements = line.split(": ")
                    informed_optimality_values.append(float(elements[1].strip()))
                if "Goals positions (uninformed clique generation) search time" in line:
                    elements = line.split(": ")
                    uninformed_times.append(float(elements[1].strip()))
                if "Goals positions (informed clique generation) search time" in line:
                    elements = line.split(": ")
                    informed_times.append(float(elements[1].strip()))
                if "Hungarian algorithm heuristic cost" in line:
                    elements = line.split(": ")
                    hungarian_heuristic_values.append(int(elements[1].strip()))
                if "Hungarian algorithm time" in line:
                    elements = line.split(": ")
                    hungarian_times.append(float(elements[1].strip()))
                if "Hungarian algorithm CBS cost" in line:
                    elements = line.split(": ")
                    if elements[1].strip() == "not found":
                        hungarian_cbs_values.append(-1)
                    else:
                        hungarian_cbs_values.append(int(elements[1].strip()))
                if "Random assignment heuristic cost" in line:
                    elements = line.split(": ")
                    random_heuristic_values.append(int(elements[1].strip()))
                if "Random assignment CBS cost" in line:
                    elements = line.split(": ")
                    if elements[1].strip() == "not found":
                        random_cbs_values.append(-1)
                    else:
                        random_cbs_values.append(int(elements[1].strip()))

    f = open("./data/number_of_cliques", "w")      
    sys.stdout = f
    for value in number_of_cliques:
        print(value)

    f = open("./data/uninformed_optimality_values", "w")      
    sys.stdout = f
    for value in uninformed_optimality_values:
        print(value)

    f = open("./data/informed_optimality_values", "w")      
    sys.stdout = f
    for value in informed_optimality_values:
        print(value)

    f = open("./data/uninformed_times", "w")      
    sys.stdout = f
    for value in uninformed_times:
        print(value)

    f = open("./data/informed_times", "w")      
    sys.stdout = f
    for value in informed_times:
        print(value)
    
    f = open("./data/hungarian_heuristic_values", "w")      
    sys.stdout = f
    for value in hungarian_heuristic_values:
        print(value)
    
    f = open("./data/hungarian_cbs_values", "w")      
    sys.stdout = f
    for value in hungarian_cbs_values:
        print(value)
    
    f = open("./data/hungarian_times", "w")      
    sys.stdout = f
    for value in hungarian_times:
        print(value)
    
    f = open("./data/random_heuristic_values", "w")      
    sys.stdout = f
    for value in random_heuristic_values:
        print(value)
    
    f = open("./data/random_cbs_values", "w")      
    sys.stdout = f
    for value in random_cbs_values:
        print(value)

    sys.stdout = sys.__stdout__

def generate_charts() -> None:
    # uninformed/informed goals generation times
    D = [[],[]]
    f = open("./data/uninformed_times", "r")      
    while True:
        line = f.readline()
        if line == "": break
        D[0].append(float(line))
    f = open("./data/informed_times", "r")      
    while True:
        line = f.readline()
        if line == "": break
        D[1].append(float(line))
    fig, ax = plt.subplots()
    ax.boxplot(D, labels=["Uninformed", "Informed"], showfliers=False)
    ax.set_title("Goals generation times")
    ax.set_ylabel("seconds")

    plt.show()

    # uninformed/informed optimality
    D = [[],[]]
    f = open("./data/uninformed_optimality_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        D[0].append(float(line))
    f = open("./data/informed_optimality_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        D[1].append(float(line))
    fig, ax = plt.subplots()
    ax.boxplot(D, labels=["Uninformed", "Informed"])
    ax.set_title("Optimality")

    plt.show()

    # uninformed/informed optimality related to number of cliques
    x = []
    y = []
    f = open("./data/uninformed_optimality_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        x.append(float(line))
    f = open("./data/number_of_cliques", "r")      
    while True:
        line = f.readline()
        if line == "": break
        y.append(int(line))

    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_title("Optimality related to number of cliques")
    ax.set_xlabel("Uninformed generation goals optimality")
    ax.set_ylabel("Number of cliques")

    plt.show()

    x = []
    f = open("./data/informed_optimality_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        x.append(float(line))

    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_title("Optimality values related to number of cliques")
    ax.set_xlabel("Informed generation goals optimality")
    ax.set_ylabel("Number of cliques")

    plt.show()

    # Hungarian algorithm execution times
    x = []
    f = open("./data/hungarian_times", "r")      
    while True:
        line = f.readline()
        if line == "": break
        x.append(float(line))
    fig, ax = plt.subplots()
    ax.hist(x, bins=8)
    ax.set_title("Hungarian algorithm execution times")
    ax.set_xlabel("seconds")

    plt.show()

    # Hungarian/random goals assignment heuristic/CBS costs
    hungarian_heuristic_costs = []
    random_heuristic_costs = []
    f = open("./data/hungarian_heuristic_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        hungarian_heuristic_costs.append(int(line))
    f = open("./data/random_heuristic_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        random_heuristic_costs.append(int(line))
    percentages = []
    for i in range(len(hungarian_heuristic_costs)):
        diff = ((random_heuristic_costs[i] - hungarian_heuristic_costs[i]) / random_heuristic_costs[i]) * 100
        percentages.append(diff)

    fig, ax = plt.subplots()
    ax.boxplot(percentages)
    ax.set_title("How much assignments found with hungarian algorithm\nare better than random assignments\nin percentage\n(heuristic cost)")

    plt.show()

    #

    hungarian_cbs_costs = []
    random_cbs_costs = []
    f = open("./data/hungarian_cbs_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        hungarian_cbs_costs.append(int(line))
    f = open("./data/random_cbs_values", "r")      
    while True:
        line = f.readline()
        if line == "": break
        random_cbs_costs.append(int(line))
    percentages = []
    for i in range(len(hungarian_cbs_costs)):
        if random_cbs_costs[i] == -1 or hungarian_cbs_costs[i] == -1:
            continue
        diff = ((random_cbs_costs[i] - hungarian_cbs_costs[i]) / random_cbs_costs[i]) * 100
        percentages.append(diff)

    fig, ax = plt.subplots()
    ax.boxplot(percentages)
    ax.set_title("How much assignments found with hungarian algorithm\n are better than random assignments\nin percentage\n(CBS cost)")

    plt.show()

aggregate_data()
generate_charts()