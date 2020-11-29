from datetime import timedelta
from enum import Enum, auto
from numpy import random

from lib.enums import TELState, TELType

class TEL:
    """A single Transporter-Erector-Launcher.
    
    TELs are not modeled as having a precise geographic location. Instead, they are
    associated with a TEL base (which does have a location), and at any given
    moment are in one out of a set of possible states (in base, roaming, hiding in a
    tunnel, etc).
    """
    
    def __init__(self, base, uid, tel_type=TELType.BASIC,
                 initial_state=TELState.IN_BASE, strategy=None):
        """Initialize a TEL object.
        
        Args:
          base: The TELBase this TEL belongs to.
          uid: Unique identifier for this TEL, unique among all TELs in the simulation.
          tel_type: A TELType enum value.
          initial_state: A TELState enum value.
          strategy: A strategy dict, from lib.tel_strategy.load_strategy. Required.
        """
        self.base = base
        self.uid = uid
        self.type = tel_type
        self.state = initial_state
        assert strategy is not None
        self.strategy = strategy
        
    def start(self, s):
        s.schedule_event_relative(lambda: self.update_state(s),
                                  timedelta(minutes=random.randint(0, 60)),
                                  repeat_interval=timedelta(minutes=60))
    
    def update_state(self, s):
        transition_probs = self.strategy[
            (self.type,
             s.alert_level,
             self.base.location.get_time_of_day(s.t),
             self.state)]
        next_state = random.choice(list(transition_probs.keys()),
                                   p=list(transition_probs.values()))
        self.state = next_state
        
    def status(self):
        return '{} TEL associated with {} Base. uid: {}, current state: {}'.format(
            self.type.name, self.base.name, self.uid, self.state.name)