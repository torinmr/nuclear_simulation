from datetime import timedelta
from enum import Enum, auto
from numpy import random
from uuid import uuid4

from lib.enums import TELState, TELKind, TELStrategy

class TEL:
    """A single Transporter-Erector-Launcher.
    
    TELs are not modeled as having a precise geographic location. Instead, they are
    associated with a TEL base (which does have a location), and at any given
    moment are in one out of a set of possible states (in base, roaming, hiding in a
    tunnel, etc).
    """
    
    def __init__(self, base, name, tel_kind=None,
                 initial_state=TELState.IN_BASE, strategies=None):
        """Initialize a TEL object.
        
        Args:
          base: The TELBase this TEL belongs to.
          name: Human readable name for this TEL.
          tel_kind: A TELKind enum value.
          initial_state: A TELState enum value.
          strategies: A strategy dict - see tel_strategy.py. Required.
        """
        self.base = base
        self.name = name
        self.uid = uuid4().int
        assert tel_kind is not None
        self.kind = tel_kind
        self.state = initial_state
        assert strategies is not None 
        self.strategies = strategies
        
    def start(self, s):
        s.schedule_event_relative(lambda: self.update_state(s),
                                  timedelta(minutes=random.randint(0, 60)),
                                  repeat_interval=timedelta(minutes=60))
        
    def choose_strategy(self, s):
        """Return a TELStrategy enum for what strategy this TEL should adopt at this timestep."""
        return TELStrategy.AGGRESSIVE
    
    def update_state(self, s):
        transition_probs = self.strategies[self.choose_strategy(s)][self.state]
        next_state = random.choice(list(transition_probs.keys()),
                                   p=list(transition_probs.values()))
        self.state = next_state
        
    def status(self):
        return '{} TEL associated with {} Base. uid: {}, current state: {}'.format(
            self.kind.name, self.base.name, self.uid, self.state.name)