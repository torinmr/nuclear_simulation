from abc import ABC, abstractmethod
from datetime import timedelta
from numpy import random

from lib.enums import DetectionMethod, TLOKind, TELState, Weather, SimulationMode, TimeOfDay
from lib.intelligence_types import Observation
from lib.location import Location
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

def truck_utilization_fraction(c, daylight_fraction):
    return (c.nighttime_truck_utilization*(1-daylight_fraction) +
            c.daytime_truck_utilization*daylight_fraction)

def daylight_fraction(t, tlo):
    if tlo.base or tlo.tel:
        location = tlo.base.location if tlo.base else tlo.tel.location
        time = location.get_time_of_day(t)
        if time == TimeOfDay.DAY:
            return 1
        elif time == TimeOfDay.NIGHT:
            return 0
    else:
        # Hack alert: To estimate the percentage of China where it's daytime, check
        # 10 locations spread at different longitudes throughout the country.
        locs = [Location(35, lon) for lon in range(78, 135, 6)]
        num_daylight = sum([1 for l in locs if l.is_day(t)])
        frac_daylight = num_daylight / len(locs)
        return frac_daylight

def weather_visibility(c, tlo):
    if tlo.base or tlo.tel:
        # Use the base's weather or local weather, depending on whether the TLO is tied
        # to a base or not.
        weather = tlo.base.weather if tlo.base else tlo.tel.weather
        if weather == Weather.CLEAR:
            return 1
        elif weather == Weather.OVERCAST:
            return 0
        elif weather == Weather.CLOUDY:
            return c.cloudy_visibility
    else:
        # Use a composite visibility score for TLOs not associated with a base or TEL.
        visibility = (1 * c.weather_probabilities[Weather.CLEAR] +
                      c.cloudy_visibility * c.weather_probabilities[Weather.CLOUDY])
        return visibility
    
def obstruction_visibility(tlo):
    # TELs and decoys in physical shelters can't be observed by satellites.
    if tlo.tel and tlo.tel.state in {TELState.IN_BASE, TELState.SHELTERING}:
        return 0
    else:
        return 1

class EOObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
        
    def observe_tlos(self, t, tlos):
        obs = []
        total_observed = 0
        for tlo in tlos:
            day_frac = daylight_fraction(t, tlo)

            p_visible = 1
            p_visible *= day_frac
            if tlo.kind == TLOKind.TRUCK:
                p_visible *= truck_utilization_fraction(self.c, day_frac)
            p_visible *= obstruction_visibility(tlo)
            p_visible *= weather_visibility(self.c, tlo)

            num_observed = random.binomial(n=tlo.multiplicity, p=p_visible)
            if num_observed > 0:
                obs.append(tlo.observe(t, DetectionMethod.EO, num_observed))
                total_observed += num_observed
        return obs, total_observed
    
    def observe(self, s):
        obs = []
        if self.c.simulation_mode == SimulationMode.BASE_LOCAL:
            for base in s.bases:
                # EOs can't see at night.
                if base.location.is_night(s.t):
                    continue

                new_obs, num_obs = self.observe_tlos(s.t, base.tlos)
                obs += new_obs
                non_tlo_obs = self.c.satellite_tiles_per_base - num_obs
                obs.append(Observation(t=s.t, method=DetectionMethod.EO,
                                       multiplicity=non_tlo_obs))
        elif self.c.simulation_mode == SimulationMode.FREE_ROAMING:
            new_obs, num_obs = self.observe_tlos(s.t, s.free_tlos)
            obs += new_obs
            non_tlo_obs = self.c.satellite_tiles - num_obs
            obs.append(Observation(t=s.t, method=DetectionMethod.EO,
                                   multiplicity=non_tlo_obs))
        return obs

def sar_visibility(c, t, tlo):
    if tlo.base or tlo.tel:
        offset = tlo.base.sar_offset if tlo.base else tlo.tel.sar_offset
        current_offset = ((t - offset) / timedelta(minutes=1)) % c.sar_cadence_min
        if current_offset < c.sar_duration_min:
            return 1
        else:
            return 0
    else:
        return c.sar_uptime
    
class SARObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
        
    def observe_tlos(self, t, tlos):
        obs = []
        total_observed = 0
        for tlo in tlos:
            day_frac = daylight_fraction(t, tlo)
            p_visible = 1
            p_visible *= sar_visibility(self.c, t, tlo)
            if tlo.kind == TLOKind.TRUCK:
                p_visible *= truck_utilization_fraction(self.c, day_frac)
            p_visible *= obstruction_visibility(tlo)
            
            num_observed = random.binomial(n=tlo.multiplicity, p=p_visible)
            if num_observed > 0:
                obs.append(tlo.observe(t, DetectionMethod.SAR, num_observed))
                total_observed += num_observed
        return obs, total_observed
    
    def observe(self, s):
        obs = []
        if self.c.simulation_mode == SimulationMode.BASE_LOCAL:
            for base in s.bases:
                if sar_visibility(self.c, s.t, base.tlos[0]) > 0:
                    new_obs, num_obs = self.observe_tlos(s.t, base.tlos)
                    obs += new_obs
                    non_tlo_obs = self.c.satellite_tiles_per_base - num_obs
                    obs.append(Observation(t=s.t, method=DetectionMethod.SAR,
                                            multiplicity=non_tlo_obs))
        elif self.c.simulation_mode == SimulationMode.FREE_ROAMING:
            new_obs, num_obs = self.observe_tlos(s.t, s.free_tlos)
            obs += new_obs
            non_tlo_obs = self.c.satellite_tiles * self.c.sar_uptime - num_obs
            obs.append(Observation(t=s.t, method=DetectionMethod.SAR,
                                   multiplicity=non_tlo_obs))
        return obs

    
def offshore_visibility(c, tlo):
    if tlo.base:
        return tlo.base.offshore_observability
    elif tlo.tel:
        return 1 if tlo.tel.near_shore else 0
    else:
        return c.offshore_observability

class StandoffObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
        
    def observe_tlos(self, t, tlos):
        obs = []
        total_observed = 0
        for tlo in tlos:
            day_frac = daylight_fraction(t, tlo)
            p_visible = 1
            p_visible *= offshore_visibility(self.c, tlo)
            if tlo.kind == TLOKind.TRUCK:
                p_visible *= truck_utilization_fraction(self.c, day_frac)
            p_visible *= obstruction_visibility(tlo)
            
            num_observed = random.binomial(n=tlo.multiplicity, p=p_visible)
            if num_observed > 0:
                obs.append(tlo.observe(t, DetectionMethod.OFFSHORE_SAR, num_observed))
                total_observed += num_observed
        return obs, total_observed
    
    def observe(self, s):
        obs = []
        if self.c.simulation_mode == SimulationMode.BASE_LOCAL:
            for base in s.bases:
                offshore_vis = offshore_visibility(self.c, base.tlos[0])
                if offshore_vis > 0:
                    new_obs, num_obs = self.observe_tlos(s.t, base.tlos)
                    obs += new_obs
                    non_tlo_obs = self.c.satellite_tiles_per_base * offshore_vis - num_obs
                    obs.append(Observation(t=s.t, method=DetectionMethod.OFFSHORE_SAR,
                                            multiplicity=non_tlo_obs))
        elif self.c.simulation_mode == SimulationMode.FREE_ROAMING:
            new_obs, num_obs = self.observe_tlos(s.t, s.free_tlos)
            obs += new_obs
            non_tlo_obs = self.c.satellite_tiles * self.c.offshore_observability - num_obs
            obs.append(Observation(t=s.t, method=DetectionMethod.OFFSHORE_SAR,
                                   multiplicity=non_tlo_obs))
        return obs
    
class SigIntObserver(Observer):
    def __init__(self, c):
        super().__init__(c)
        
    def observe(self, s):
        obs = []
        for tlo in s.tlos():
            if tlo.tel and not tlo.tel.emcon:
                offset = hash(tlo.tel.name + 'SIGINT') % 60
                if s.t.minute == offset and random.random() < self.c.sigint_hourly_detect_chance:
                    print("Observed {}".format(tlo.tel.name))
                    obs.append(tlo.observe(s.t, DetectionMethod.SIGINT, 1))
        return obs