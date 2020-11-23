from datetime import timedelta
from enum import Enum, auto
import random

from lib.enums import TELState, TELType

class TEL:
    """A single Transporter-Erector-Launcher.
    
    TELs are not modeled as having a precise geographic location. Instead, they are
    associated with a TEL base (which does have a location), and at any given
    moment are in one out of a set of possible states (in base, roaming, hiding in a
    tunnel, etc).
    """
    
    def __init__(self, base, tel_type=TELType.BASIC,
                 initial_state=TELState.IN_BASE, strategies=None):
        """Initialize a TEL object.
        
        Args:
          base: The TELBase this TEL belongs to.
          tel_type: A TELType enum value.
          initial_state: A TELState enum value.
          strategies: A strategy dict, from lib.tel_strategy.load_strategies. Required.
        """
        self.base = base
        self.type = tel_type
        self.state = initial_state
        self.s = base.s
        self.s.schedule_event_relative(self.update_state,
                                       timedelta(minutes=random.randrange(60)),
                                       repeat_interval=timedelta(minutes=60))
        assert strategies is not None
        self.strategies = strategies
    
    def update_state(self):
        transition_probs = self.strategies[
            (self.type,
             self.s.alert_level,
             self.base.location.get_time_of_day(self.s.t),
             self.state)]
        next_state = random.choices(list(transition_probs.keys()),
                                    list(transition_probs.values()))[0]
        self.state = next_state
        
    def status(self):
        return '{} TEL associated with {} Base, current state: {}'.format(
            self.type.name, self.base.name, self.state.name)