from abc import ABC, abstractmethod

from lib.enums import TLOKind
from lib.intelligence_types import File
       
class Tracker:
    def __init__(self):
        super().__init__()
        self.files = {}
        
    def start(self, s):
        for tel in s.tels():
            self.files[tel.uid] = File(tel.uid)
               
    @abstractmethod
    def assign_observations(self, observations):
        """Assign observations to files."""
        pass
        
class PerfectTracker(Tracker):
    def __init__(self):
        super().__init__()

    def assign_observations(self, observations):
        for obs in observations:
            if obs.uid in self.files:
                self.files[obs.uid].add_observation(obs)
    
class RealisticTracker(Tracker):
    def __init__(self):
        super().__init__()

    def assign_observations(self, observations):
        pass
    
        
        
        