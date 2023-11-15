from enum import Enum

class GoalsChoice(Enum):
    GREEDY = 1
    COMPLETE = 2
    IMPROVED_COMPLETE = 3
    MINIMIZE_MEAN_DISTANCE = 4

class GoalsAssignment(Enum):
    ARBITRARY = 1
    RANDOM = 2
    GREEDY = 3
    EXHAUSTIVE_SEARCH = 4
    LOCAL_SEARCH = 5

class ConnectionCriterion(Enum):
    NONE = 1
    DISTANCE = 2
    PATH_LENGTH = 3