from abc import ABC, abstractmethod
from numpy import random

from lib.enums import DetectionMethod, TLOKind, TELState
from lib.intelligence_types import Observation

class Observer(ABC):
    def __init__(self, c):
        self.c = c
        super().__init__()
    
    @abstractmethod
    def observe(self, s):
        """Observe the current state of the simulation, and emit observations.
        
        Args:
          s: The simulation object.
        Returns:
          A collection of Observations representing unprocessed sensor data. Should
          include both positive observations (corresponding to any and all TELs this
          Observer can observe at the moment), and negative observations (corresponding
          to satellite images containing no TELs, for example).
        """  
        pass

def truck_utilization_fraction(tlo, s, c):
    if tlo.base.location.is_night(s.t):
        return c.nighttime_truck_utilization
    elif tlo.base.location.is_day(s.t):
        return c.daytime_truck_utilization
    else:
        print("Warning: Unknown time of day.")
        return 0

class EOObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
    
    def observe(self, s):
        observations = []
        num_observations = 0
        for tlo in s.tlos():
            base = tlo.base
            p_visible = 1
            
            # EOs can't see at night.
            if base.location.is_night(s.t):
                p_visible *= 0
                
            # Not all trucks are on the road at the same time.
            if tlo.kind == TLOKind.TRUCK:
                p_visible *= truck_utilization_fraction(tlo, s, self.c)

            # TELs and decoys in physical shelters can't be observed by satellites.
            if tlo.tel and tlo.tel.state in {TELState.IN_BASE, TELState.SHELTERING}:
                p_visible *= 0
            
            # Remaining TELs may be obscured by clouds.
            p_visible *= (1 - base.cloud_cover)

            num_observed = random.binomial(n=tlo.multiplicity, p=p_visible)
            if num_observed > 0:
                observations.append(tlo.observe(s.t, DetectionMethod.EO, num_observed))
                num_observations += num_observed

        non_tlo_observations = self.c.total_eo_tiles - num_observations
        observations.append(Observation(t=s.t, method=DetectionMethod.EO,
                                        multiplicity=non_tlo_observations))
        return observations

class SARObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
    
    def observe(self, s):
        return []