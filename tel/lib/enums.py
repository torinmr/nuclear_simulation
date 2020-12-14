from enum import IntEnum, auto

class TimeOfDay(IntEnum):
    DAY = auto()
    NIGHT = auto()
    
class Weather(IntEnum):
    CLEAR = auto()          # Full visibility.
    CLOUDY = auto()         # 50% chance of seeing a given TEL at a given timestep.
    OVERCAST = auto()       # No visibility.
    
class TELState(IntEnum):
    IN_BASE = auto()        # TEL is parked in a base (not visible to satellites)
    LEAVING_BASE = auto()   # TEL is preparing to leave (visible to satellites)
    ROAMING = auto()        # TEL is roaming
    ARRIVING_BASE = auto()  # TEL is arriving at a base (visible to satellites)
    REFUELING = auto()      # TEL is refueling and performing maintenance (visible to satellites).
                            #   Only applicable during high alert (TELs refuel at base otherwise).
    SHELTERING = auto()     # TEL is sheltering under a thick structure away from base. Only
                            #   applicable during high alert.

class TELKind(IntEnum):
    DF_31A = auto()
    DF_31AG = auto()
    DF_26 = auto()
    DF_31 = auto()
    DF_21AE = auto()
    
class DetectionMethod(IntEnum):
    INITIAL = auto()  # Location is assumed known at the beginning of the simulation.
    EO = auto()
    SAR = auto()
    OFFSHORE_SAR = auto()
    SIGINT = auto()
    
class TLOKind(IntEnum):
    TEL = auto()           # A real TEL.
    TRUCK = auto()         # A normal truck that could be mistaken for a TEL.
    DECOY = auto()         # A decoy intentionally made to look like a TEL.
    SECRET_DECOY = auto()  # A special decoy that the US is assumed not to have previous knowledge of.

# Mode used for simulating TEL roaming, set at the simulation level. Determines how effects like
# weather are simulated, and how the number of potential false positive objects are calculated.
class SimulationMode(IntEnum):
    BASE_LOCAL = auto()    # TELs stay within a range of their base.
    FREE_ROAMING = auto()  # TELs can roam over all of China.