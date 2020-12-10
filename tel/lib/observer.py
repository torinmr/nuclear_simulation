from abc import ABC, abstractmethod
from numpy import random

from lib.enums import DetectionMethod
from lib.intelligence_types import Observation

class Observer(ABC):
    def __init__(self):
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
    def __init__(self):
        super().__init__()
    
    def observe(self, s):       
        # TODO(Ben): Is there any natural delay (> 1 minute) in collecting
        #   satellite images and transmitting them to the US for analysis?
        observations = []
        for tel in s.tels():
            base = tel.base
            if base.location.is_night(s.t):
                continue
            # With 70% cloud cover, each TEL has a 30% chance of being visible.
            if random.random() < base.cloud_cover:
                continue
            observations.append(Observation(s.t, tel.uid, method=DetectionMethod.EO))
        
        # TODO: How does this interact with TEL state? Do we assume that when
        #   they're in the base they're easily visible, or totally invisible
        #   (if they're in a bunker or something).
        observations.append(Observation(s.t, None, multiplicity=20_000_000,
                                        method=DetectionMethod.EO))
        return observations

class SARObserver(Observer):
    def __init__(self):
        super().__init__()
    
    def observe(self, s):
        return []