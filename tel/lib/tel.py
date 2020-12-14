from datetime import timedelta
from enum import Enum, auto
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
        
        self.mated = random.random() < c.mating_fraction
        
    def update_weather(self):
        self.weather = Weather(random.choice(list(self.c.weather_probabilities.keys()),
                                             p=list(self.c.weather_probabilities.values())))
        #print("Weather around {} is now {}".format(self.name, self.weather.name))
        
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
        
    
    def update_state(self, s, state):
        #print("{}: {} -> {}".format(format_time(s.t), self.name, state.name))
        self.state = state
        self.emcon = random.random() < self.c.emcon_fraction
                
    def status(self):
        if self.base:
            return '{} {} associated with {} Base. uid: {}, current state: {}'.format(
                self.kind.name, self.tlo_kind.name,
                self.base.name, self.uid, self.state.name)
        else:
            return '{} {}. uid: {}, current state: {}, weather: {}'.format(
                self.kind.name, self.tlo_kind.name, self.uid, self.state.name, self.weather.name)
            