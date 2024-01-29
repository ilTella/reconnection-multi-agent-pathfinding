from enum import Enum

class GoalsChoice(Enum):
    UNINFORMED_GENERATION = 1
    INFORMED_GENERATION = 2

class GoalsAssignment(Enum):
    HUNGARIAN = 1
    LOCAL_SEARCH = 2
    RANDOM = 3

class ConnectionCriterion(Enum):
    NONE = 1
    DISTANCE = 2
    PATH_LENGTH = 3