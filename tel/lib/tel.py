from datetime import timedelta
from enum import Enum, auto
import math
from numpy import random
from uuid import uuid4

from lib.enums import TELState, TLOKind, TELKind, SimulationMode, Weather
from lib.intelligence_types import TLO
from lib.location import random_location
from lib.time import format_time

class TEL:
    """A single Transporter-Erector-Launcher.
    
    TELs are not modeled as having a precise geographic location. Instead, they are
    associated with a TEL base (which does have a location), and at any given
    moment are in one out of a set of possible states (in base, roaming, hiding in a
    tunnel, etc).
    """
    
    def __init__(self, c, base, name, tel_kind=None, tlo_kind=None, is_decoy=False):
        """Initialize a TEL object.
        
        Args:
          c: Config object.
          base: The TELBase this TEL belongs to. None for free-roaming TELs.
          name: Human readable name for this TEL.
          tel_kind: A TELKind enum value.
          tlo_kind: A TLOKind enum (indicating whether this is a TEL or a decoy).
        """
        self.c = c
        self.base = base
        self.name = name
        self.uid = uuid4().int
        assert tel_kind is not None
        self.kind = tel_kind
        self.tlo_kind = tlo_kind
        if not self.base:
            self.update_weather()
            self.update_shore()
            # Hack alert: Give non-base TELs a random location somewhere vaguely in China,
            # so that they can have a realistic distribution of sunrise times.
            self.location = random_location()

        # For the schedule stored in the TEL object, we use the format (offset, state),
        # where offsets are relative to the loop time and shifted randomly for each TEL.
        self.loop_time = timedelta()
        for (duration, _) in c.tel_schedule:
            self.loop_time += duration
        offset = timedelta(minutes=random.randint(self.loop_time / timedelta(minutes=1)))
        self.offset_schedule = []
        for (duration, state) in c.tel_schedule:
            if offset >= self.loop_time:
                offset -= self.loop_time
            assert offset < self.loop_time
            self.offset_schedule.append((offset, state))
            offset += duration
        # Sorting the schedule has the effect of rotating the order of states around based
        # on the current offset.
        self.offset_schedule.sort()
        
        self.state_history = []
        self.mated = random.random() < c.mating_fraction
        
    def update_weather(self):
        self.weather = Weather(random.choice(list(self.c.weather_probabilities.keys()),
                                             p=list(self.c.weather_probabilities.values())))
        #print("Weather around {} is now {}".format(self.name, self.weather.name))
        
    def update_shore(self):
        self.near_shore = random.random() < self.c.offshore_observability
        
    def start(self, s):
        if self.offset_schedule[0][0] == timedelta():
            self.update_state(s, self.offset_schedule[0][1])
        else:
            self.update_state(s, self.offset_schedule[-1][1])

        for offset, state in self.offset_schedule:
            s.schedule_event_relative(lambda state=state: self.update_state(s, state),
                                      offset, repeat_interval=self.loop_time)
            
        if not self.base:
            frequency = self.c.weather_change_frequency
            offset = timedelta(minutes=random.randint(frequency / timedelta(minutes=1)))
            s.schedule_event_relative(self.update_weather, offset, repeat_interval=frequency)
            
            offset_mins = hash(self.name + "SAR") % self.c.sar_cadence_min
            self.sar_offset = s.t + timedelta(minutes=offset_mins)  
            
            frequency = self.c.offshore_change_frequency
            offset = timedelta(minutes=random.randint(frequency / timedelta(minutes=1)))
            s.schedule_event_relative(self.update_shore, offset, repeat_interval=frequency)
        
    
    def update_state(self, s, state):
        self.state = state
        self.state_history.append((s.t, state))
        self.emcon = random.random() < self.c.emcon_fraction
        self.ground_sensor_attempted = False
                
    def status(self):
        if self.base:
            return '{} {} associated with {} Base. uid: {}, current state: {}'.format(
                self.kind.name, self.tlo_kind.name,
                self.base.name, self.uid, self.state.name)
        else:
            return '{} {}. uid: {}, current state: {}, weather: {}'.format(
                self.kind.name, self.tlo_kind.name, self.uid, self.state.name, self.weather.name)
    
    def roaming_time_since_observation(self, obs, current_t):
        """How long the TEL has been roaming since the observation."""
        last_state = None
        last_t = obs.t
        roam_time = timedelta()
        for (t, state) in self.state_history + [(current_t, None)]:
            if t > last_t:
                if last_state == TELState.ROAMING:
                    roam_time += t - last_t
                last_state = state
                last_t = t
            last_state = state
        return roam_time
            
    def destruction_area(self, obs, current_t, target_t):
        """km2 that must be destroyed to destroy this TEL.
        
        Args:
          obs: Last known observation of this TEL.
          target_t: Time missile will land (not necessary current time).
        """
        # TELs that are in a base (and not leaving soon) are destroyed when the base is blown up, no
        # extra missiles needed.
        if self.state in {TELState.IN_BASE, TELState.ARRIVING_BASE}:
            return -1
        
        # Significant simplification:
        # I am only calculating how much time the TEL *did in fact spend roaming* since it was last
        # observed. In cases where the TEL went into a shelter the US may actually have a large
        # degree of uncertainty about this. E.g. suppose that since observation, the TEL drove for
        # 10 minutes, then hid in an overpass for 3 hours and is still there. The US would just know
        # it hasn't seen it for 3 hours 10 mins, and could maybe guess it had stopped, but wouldn't
        # really know. This calculation gives the US credit for knowing it only drove 10 minutes.
        roam_time = self.roaming_time_since_observation(obs, current_t)
        roam_time += target_t - current_t
        
        roam_dist = self.c.tel_speed_kmph * (roam_time / timedelta(hours=1))
        roam_area = math.pi * roam_dist**2
        return roam_area * self.c.destruction_area_factor