from abc import ABC, abstractmethod
from datetime import timedelta

from lib.enums import TLOKind, DetectionMethod
from lib.intelligence_types import File, Observation
       
class Tracker:
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.files = {}
        
    def start(self, s):
        for tel in s.tels():
            initial_obs = Observation(s.t, DetectionMethod.INITIAL, tel.uid,
                                      tel.state, tlo_kind=TLOKind.TEL)
            self.files[tel.uid] = File(uid=tel.uid, tel=tel, obs=[initial_obs])
               
    @abstractmethod
    def assign_observations(self, observations):
        """Assign observations to files."""
        pass
    
    def analyze_files(self, t):
        for f in self.files.values():
            f.obs.sort()
            obs = f.obs[-1]
            print("Latest observation of TEL {} was {} minutes ago by {} in state {}, current state {}.".format(
                f.tel.name, (t - obs.t)/timedelta(minutes=1), obs.method.name,
                obs.state.name, f.tel.state.name))
        
class PerfectTracker(Tracker):
    def __init__(self, c):
        super().__init__(c)

    def assign_observations(self, observations):
        for obs in observations:
            if obs.uid in self.files:
                self.files[obs.uid].add_observation(obs)
    
class RealisticTracker(Tracker):
    def __init__(self, c):
        super().__init__(c)

    def assign_observations(self, observations):
        pass
    
        
        
        