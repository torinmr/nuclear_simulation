from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional, FrozenSet, List, Tuple

from lib.enums import TELKind, TELState

@dataclass
class DefaultConfig:
    # TEL kinds relevant to the simulation. If provided, TEL kinds not on the
    # list are not simulated and not tracked by the US.
    tel_kinds: Optional[FrozenSet[TELKind]] = None
        
    # Fraction of TELs mated (armed with a nuclear warhead) at any given time.
    mating_fraction: float = 1
        
    # Schedule that each TEL will independently repeat in a loop (at staggered intervals).
    tel_schedule: List[Tuple[timedelta, TELState]] = field(default_factory=list)
        
    # TEL speed (in km/h).
    tel_speed_kmph: float = 20
    
    # Fraction of time that TELs practice emissions control (radio silence).
    # A TEL decides to practice EMCON at the beginning of each state transition, doesn't change its mind
    # until the next state transition.
    emcon_fraction: float = 0
        
    # Ratio of decoys to real TELs. These represent "normal" decoys the US has prior intelligence about.
    decoy_ratio: float = 0
        
    # Ratio of secret decoys to real TELs. These represent special decoys only deployed in a crisis, so
    # the US is worse at distinguishing them.
    secret_decoy_ratio: float = 0
        
    # Files containing external data.
    bases_filename: str = 'data/tel_bases.csv'

@dataclass
class LowAlert(DefaultConfig):
    mating_fraction: float = 1/6
    tel_schedule: List[Tuple[timedelta, TELState]] = field(default_factory=lambda: [
        # 8 hours roaming, 32 hours in base. 25% roaming time overall.
        (timedelta(hours=23), TELState.IN_BASE),
        (timedelta(minutes=30), TELState.LEAVING_BASE),
        (timedelta(hours=8), TELState.ROAMING),
        (timedelta(minutes=30), TELState.ARRIVING_BASE),
    ])
    tel_speed_kmph: float = 20
    emcon_fraction: float = 0
    decoy_ratio: float = 0
    secret_decoy_ratio: float = 0
        
@dataclass
class MediumAlert(DefaultConfig):
    mating_fraction: float = .5
    tel_schedule: List[Tuple[timedelta, TELState]] = field(default_factory=lambda: [
        # 16 hours roaming, 5 hours 20 minutes in base. 75% roaming time overall.
        (timedelta(hours=4, minutes=20), TELState.IN_BASE),
        (timedelta(minutes=30), TELState.LEAVING_BASE),
        (timedelta(hours=16), TELState.ROAMING),
        (timedelta(minutes=30), TELState.ARRIVING_BASE),
    ])
    tel_speed_kmph: float = 40
    emcon_fraction: float = .5
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 0

@dataclass
class HighAlert(DefaultConfig):
    mating_fraction: float = 1
    tel_schedule: List[Tuple[timedelta, TELState]] = field(default_factory=lambda: [
        # 20 hours/day of driving (including one mid-day refueling stop), 4 hours/day sheltering.
        (timedelta(hours=9, minutes=45), TELState.ROAMING),
        (timedelta(minutes=30), TELState.REFUELING),
        (timedelta(hours=9, minutes=45), TELState.ROAMING),
        (timedelta(hours=4), TELState.SHELTERING),
    ])
    tel_speed_kmph: float = 69
    emcon_fraction: float = 1
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 1
        
tel_kinds_continental_us = frozenset({TELKind.DF_31A, TELKind.DF_31AG})
tel_kinds_alaska_hawaii = tel_kinds_continental_us | frozenset({TELKind.DF_31})
tel_kinds_guam = tel_kinds_alaska_hawaii | frozenset({TELKind.DF_26})
tel_kinds_us_allies = tel_kinds_guam | frozenset({TELKind.DF_21AE})