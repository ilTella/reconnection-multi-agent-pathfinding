import argparse
import os

def aggregate_data(args: list) -> None:
    optimality_values = []

    for filename in os.listdir("./testing/"):
        path = "./testing/" + filename
        with open(path, 'r') as f:
            while True:
                line = f.readline()
                if "Optimality" in line:
                    elements = line.split(": ")
                    optimality_values.append(float(elements[1].strip()))
                    break
    
    print("Instances tested: " + str(len(optimality_values)))
    sum = 0
    for v in optimality_values:
        sum += v 
    mean = sum / len(optimality_values)
    mean = round(mean, 2)
    print("Mean optimality: " + str(mean))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data aggregator')
    parser.add_argument('--visualize', type=bool, default=False,
                        help='Decide to visualize the data, defaults to ' + str(False))

    args = parser.parse_args()

    aggregate_data(args)