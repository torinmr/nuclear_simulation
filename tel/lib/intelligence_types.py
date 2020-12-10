from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
from uuid import uuid4

from lib.enums import TLOKind, TELState, DetectionMethod
from lib.tel_base import TELBase

@dataclass(frozen=True)
class TLO:   
    kind: TLOKind
        
    # A unique identifier. If kind=TEL, is equal to the TEL’s unique ID.
    # Only set for TRUCK/DECOY objects if they are being tracked by the US.
    uid: Optional[int] = None
    
    # Pointer to the base the TLO is associated with. Each base is populated
    # with a number of TLOs based on how many trucks etc. are in that area
    # of China.
    base: Optional[TELBase] = None
        
    # How many real-world objects this Python object represents. Is used to
    # let one Python object represent e.g. 100,000 trucks in the Xinjiang
    # region. When > 1,  this TLO does not have a unique ID.
    multiplicity: int = 1
        
    def __init__(kind, uid=None, base=None, multiplicity=1):
        self.kind = kind
        if multiplicity == 1 and uid is None:
            self.uid = uuid4().int
        else:
            self.uid = uid   
        self.base = base,
        self.multiplicity = multiplicity

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
    
    # How many individual observations this Observation object corresponds to.
    multiplicity: int = 1

@dataclass
class File:
    # Unique ID of the TEL this file corresponds to.
    uid: int
        
    # List of observations assigned to this file.
    obs: List[Observation] = field(default_factory=list)
        
    def add_observation(self, o):
        self.obs.append(o)

def observation_stats(obs):
    """Print stats on a collection of observations."""
    return "{} TELs observed, {} non-TEL observations".format(
        sum([o.multiplicity for o in obs if o.uid]),
        sum([o.multiplicity for o in obs if not o.uid]))

def analysis_stats(obs):
    """Print stats on a collection of observations after analysis"""
    tp = sum([o.multiplicity for o in obs if o.uid])
    otp = sum([o.original_multiplicity for o in obs if o.uid])
    tpr = tp/otp if otp else 0
    fp = sum([o.multiplicity for o in obs if not o.uid])
    ofp = sum([o.original_multiplicity for o in obs if not o.uid])
    fpr = fp/ofp if ofp else 0
    return "{}/{} ({:.2%}) TELs observed, {}/{} ({:.2%}) non-TEL observations".format(
        tp, otp, tpr, fp, ofp, fpr)