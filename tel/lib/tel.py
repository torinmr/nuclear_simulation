from datetime import timedelta
from enum import Enum, auto
from numpy import random
from uuid import uuid4

from lib.enums import TELState, TLOKind, TELKind
from lib.intelligence_types import TLO
from lib.time import format_time

class TEL:
    """A single Transporter-Erector-Launcher.
    
    TELs are not modeled as having a precise geographic location. Instead, they are
    associated with a TEL base (which does have a location), and at any given
    moment are in one out of a set of possible states (in base, roaming, hiding in a
    tunnel, etc).
    """
    
    def __init__(self, c, base, name, uid=None, tel_kind=None, is_decoy=False):
        """Initialize a TEL object.
        
        Args:
          c: Config object.
          base: The TELBase this TEL belongs to.
          name: Human readable name for this TEL.
          uid: UUID. One will be generated if None.
          tel_kind: A TELKind enum value.
          is_decoy: Whether this TEL is a decoy.
        """
        self.c = c
        self.base = base
        self.name = name
        self.uid = uuid4().int if uid is None else uid
        assert tel_kind is not None
        self.kind = tel_kind
        self.is_decoy = is_decoy

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
        
    def to_tlo(self):
        kind = TLOKind.DECOY if self.is_decoy else TLOKind.TEL
        return TLO(kind=kind, tel=self, uid=self.uid, base=self.base)
        
    def start(self, s):
        if self.offset_schedule[0][0] == timedelta():
            self.update_state(s, self.offset_schedule[0][1])
        else:
            self.update_state(s, self.offset_schedule[-1][1])

        for offset, state in self.offset_schedule:
            s.schedule_event_relative(lambda state=state: self.update_state(s, state),
                                      offset, repeat_interval=self.loop_time)
        
    
    def update_state(self, s, state):
        print("{}: {} -> {}".format(format_time(s.t), self.name, state))
        self.state = state
        self.emcon = random.random() < self.c.emcon_fraction
                
    def status(self):
        return '{}{} TEL associated with {} Base. uid: {}, current state: {}'.format(
            '(decoy) ' if self.is_decoy else '', self.kind.name,
            self.base.name, self.uid, self.state.name)