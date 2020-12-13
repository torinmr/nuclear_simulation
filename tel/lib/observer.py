from abc import ABC, abstractmethod
from datetime import timedelta
from numpy import random

from lib.enums import DetectionMethod, TLOKind, TELState, Weather
from lib.intelligence_types import Observation
from lib.time import format_time

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

def weather_visibility(c, base):
    if base.weather == Weather.CLEAR:
        return 1
    elif base.weather == Weather.OVERCAST:
        return 0
    elif base.weather == Weather.CLOUDY:
        return c.cloudy_visibility
    
class EOObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
    
    def observe(self, s):
        observations = []
        num_observations = 0
        for base in s.bases:
            # EOs can't see at night.
            if base.location.is_night(s.t):
                continue
                
            # Or when it's too cloudy.
            weather_visibility_prob = weather_visibility(self.c, base)
            if  weather_visibility_prob == 0:
                continue

            for tlo in base.tlos:
                p_visible = 1

                # Not all trucks are on the road at the same time.
                if tlo.kind == TLOKind.TRUCK:
                    p_visible *= truck_utilization_fraction(tlo, s, self.c)

                # TELs and decoys in physical shelters can't be observed by satellites.
                if tlo.tel and tlo.tel.state in {TELState.IN_BASE, TELState.SHELTERING}:
                    p_visible *= 0

                # Remaining TELs may be obscured by clouds.
                p_visible *= weather_visibility_prob

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
        observations = []
        for base in s.bases:
            sar_offset = hash(base.name + "SAR") % self.c.sar_cadence_min
            current_offset = ((s.t - s.start_t) / timedelta(minutes=1)) % self.c.sar_cadence_min
            if sar_offset != current_offset:
                continue
            
            print("SAR satellite passing over {} at time {}".format(base.name, format_time(s.t)))
            
            num_observations = 0
            for tlo in base.tlos:
                p_visible = 1

                # Not all trucks are on the road at the same time.
                if tlo.kind == TLOKind.TRUCK:
                    p_visible *= truck_utilization_fraction(tlo, s, self.c)

                # TELs and decoys in physical shelters can't be observed by satellites.
                if tlo.tel and tlo.tel.state in {TELState.IN_BASE, TELState.SHELTERING}:
                    p_visible *= 0

                num_observed = random.binomial(n=tlo.multiplicity, p=p_visible)
                if num_observed > 0:
                    observations.append(tlo.observe(s.t, DetectionMethod.SAR, num_observed))
                    num_observations += num_observed
            
            non_tlo_observations = self.c.per_base_sar_tiles - num_observations
            observations.append(Observation(t=s.t, method=DetectionMethod.EO,
                                            multiplicity=non_tlo_observations))
        return observations
        