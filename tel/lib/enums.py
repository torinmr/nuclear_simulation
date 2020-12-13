from enum import Enum, auto

class TimeOfDay(Enum):
    DAY = auto()
    NIGHT = auto()
    
class TELState(Enum):
    IN_BASE = auto()        # TEL is parked in a base (not visible to satellites)
    LEAVING_BASE = auto()   # TEL is preparing to leave (visible to satellites)
    ROAMING = auto()        # TEL is roaming
    ARRIVING_BASE = auto()  # TEL is arriving at a base (visible to satellites)
    REFUELING = auto()      # TEL is refueling and performing maintenance (visible to satellites).
                            #   Only applicable during high alert (TELs refuel at base otherwise).
    SHELTERING = auto()     # TEL is sheltering under a thick structure away from base. Only
                            #   applicable during high alert.

class TELKind(Enum):
    DF_31A = auto()
    DF_31AG = auto()
    DF_26 = auto()
    DF_31 = auto()
    DF_21AE = auto()
    
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