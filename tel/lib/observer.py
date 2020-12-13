from abc import ABC, abstractmethod
from numpy import random

from lib.enums import DetectionMethod
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
    
class EOObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
    
    def observe(self, s):       
        # TODO(Ben): Is there any natural delay (> 1 minute) in collecting
        #   satellite images and transmitting them to the US for analysis?
        observations = []
        num_observations = 0
        # TODO: Take account of state, not all trucks being on the road, etc.
        for tlo in s.tlos():
            base = tlo.base
            if base.location.is_night(s.t):
                continue
            p_visible = 1 - base.cloud_cover
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