from enum import Enum


class Route(str, Enum):
    depression = "depression"
    anxiety = "anxiety"
    neither = "end"


class ProgressEnum(str, Enum):
    improving = "Improving"
    plateau = "Plateau"
    deteriorating = "Deteriorating"
