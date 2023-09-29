from enum import Enum

class GoalsChoice(Enum):
    RANDOM = 1
    MINIMIZE_DISTANCE = 2

class GoalsAssignment(Enum):
    RANDOM = 1
    MINIMIZE_DISTANCE = 2

class ConnectionCriterion(Enum):
    NONE = 1
    DISTANCE = 2
    DISTANCE_AND_OBSTACLES = 3

class ConnectionRequirement(Enum):
    DIRECT = 1
    INDIRECT = 2