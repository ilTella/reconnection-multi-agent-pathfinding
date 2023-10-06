from enum import Enum

class GoalsChoice(Enum):
    GREEDY_MINIMIZE_DISTANCE = 1            # incomplete, suboptimal

class GoalsAssignment(Enum):
    ARBITRARY = 1                           # suboptimal
    RANDOM = 2                              # suboptimal
    GREEDY_MINIMIZE_DISTANCE = 3            # suboptimal

class ConnectionCriterion(Enum):
    NONE = 1
    DISTANCE = 2
    PATH_LENGTH = 3