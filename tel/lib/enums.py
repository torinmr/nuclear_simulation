from enum import Enum, auto

class TimeOfDay(Enum):
    DAY = auto()
    NIGHT = auto()
    
class TELState(Enum):
    IN_BASE = auto()
    ROAMING = auto()

class TELType(Enum):
    # TODO: Learn actual types of TELs.
    BASIC = auto()

class AlertLevel(Enum):
    PEACETIME = auto()
    HIGH_ALERT = auto()
    
class DetectionMethod(Enum):
    # Location is assumed known at the beginning of the simulation.
    INITIAL = auto()
    EO = auto()
    SAR = auto()