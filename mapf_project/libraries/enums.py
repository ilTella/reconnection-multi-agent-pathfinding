from enum import Enum

class GoalsChoice(Enum):
    COMPLETE = 1
    IMPROVED_COMPLETE = 2
    MINIMIZE_MEAN_DISTANCE = 3

class GoalsAssignment(Enum):
    EXHAUSTIVE_SEARCH = 1
    HUNGARIAN_ALGORITHM = 2
    LOCAL_SEARCH = 3

class ConnectionCriterion(Enum):
    NONE = 1
    DISTANCE = 2
    PATH_LENGTH = 3