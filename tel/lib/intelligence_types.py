from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
from uuid import uuid4

from numpy import random

from lib.enums import TLOKind, TELState, DetectionMethod
if TYPE_CHECKING:
    from lib.tel_base import TELBase
    from lib.tel import TEL

@dataclass(frozen=True)
class TLO:   
    kind: TLOKind
        
    # A unique identifier. If kind=TEL, is equal to the TEL’s unique ID.
    # Only set for TRUCK objects if they are being tracked by the US.
    uid: Optional[int] = None
      
    # Convenience pointer to the corresponding TEL object, if applicable.
    tel: Optional[TEL] = None
    
    # Pointer to the base the TLO is associated with. Each base is populated
    # with a number of TLOs based on how many trucks etc. are in that area
    # of China.
    base: Optional[TELBase] = None
        
    # How many real-world objects this Python object represents. Is used to
    # let one Python object represent e.g. 100,000 trucks in the Xinjiang
    # region. When > 1,  this TLO does not have a unique ID.
    multiplicity: int = 1
        
    # Hacky implementation using object.__setattr__() is necessary, because
    # frozen=True prevents setting attributes normally.
    def __init__(self, kind, tel=None, uid=None, base=None, multiplicity=1):
        object.__setattr__(self, 'kind', kind)
        object.__setattr__(self, 'tel', tel)
        if multiplicity == 1 and uid is None:
            object.__setattr__(self, 'uid', uuid4().int)
        else:
            object.__setattr__(self, 'uid', uid)   
        object.__setattr__(self, 'base', base)
        object.__setattr__(self, 'multiplicity', multiplicity)
        
    def observe(self, t, method, multiplicity):
        """Create an Observation corresponding to this TLO."""
        state = self.tel.state if self.tel is not None else None
        return Observation(t=t, method=method, uid=self.uid,
                           state=state, tlo_kind=self.kind, multiplicity=multiplicity)

# Observations are immutable, and are ordered by their associated time. So,
# a list of observations can be put in chronological order by sorting.
@dataclass(frozen=True, order=True)
class Observation:
    # Timestamp of when the observation occurred.
    t: datetime 
    method: DetectionMethod
        
    # If set, the uid of the TLO this observation corresponds to.
    # If None, then this observation does not correspond to a TLO.
    uid: Optional[int] = None
        
    # State of the observed TEL, if applicable.
    state: Optional[TELState] = None
        
    # Kind of the corresponding TLO, if applicable.
    tlo_kind: TLOKind = None
    
    # How many individual observations this Observation object corresponds to.
    multiplicity: int = 1
        
    def sample(self, p):
        """Return a copy of this observation, with multiplicity adjusted according to p, or None."""
        multiplicity = random.binomial(n=self.multiplicity, p=p)
        if multiplicity > 0:
            return Observation(t=self.t, method=self.method, uid=self.uid, state=self.state,
                               tlo_kind=self.tlo_kind, multiplicity=multiplicity)
        else:
            return None

@dataclass
class File:
    # Unique ID of the TEL this file corresponds to.
    uid: int
        
    # Convenience pointer to the TEL this file corresponds to.
    tel: TEL
        
    # List of observations assigned to this file.
    obs: List[Observation] = field(default_factory=list)
        
    def add_observation(self, o):
        self.obs.append(o)