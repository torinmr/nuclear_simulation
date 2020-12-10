from enum import Enum, auto

class TimeOfDay(Enum):
    DAY = auto()
    NIGHT = auto()
    
class TELState(Enum):
    IN_BASE = auto()
    ROAMING = auto()

class TELKind(Enum):
    DF_31A = auto()
    DF_31AG = auto()
    DF_26 = auto()
    DF_31 = auto()
    DF_21AE = auto()

class AlertLevel(Enum):
    PEACETIME = auto()
    HIGH_ALERT = auto()
    
class DetectionMethod(Enum):
    # Location is assumed known at the beginning of the simulation.
    INITIAL = auto()
    EO = auto()
    SAR = auto()
    
class TLOKind(Enum):
    # A normal truck that could be mistaken for a TEL.
    TRUCK = auto()
    # A decoy intentionally made to look like a TEL.
    DECOY = auto()
    # A real TEL.
    TEL = auto()