from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional, FrozenSet

from lib.enums import TELKind

@dataclass
class DefaultConfig:
    # TEL kinds relevant to the simulation. If provided, TEL kinds not on the
    # list are not simulated and not tracked by the US.
    tel_kinds: Optional[FrozenSet[TELKind]] = None
        
    # Fraction of TELs mated (armed with a nuclear warhead) at any given time.
    mating_fraction: float = 1
        
    # Fraction of TELs roaming at a given time.
    roam_fraction: float = 1
        
    # Maximum duration of time a TEL can roam for.
    max_roam_duration: timedelta = timedelta()
        
    # TEL speed (in km/h).
    tel_speed_kmph: float = 20
    
    # Fraction of time that TELs practice emissions control (radio silence).
    emcon_fraction: float = 0
        
    # Ratio of decoys to real TELs. These represent "normal" decoys the US has prior intelligence about.
    decoy_ratio: float = 0
        
    # Ratio of secret decoys to real TELs. These represent special decoys only deployed in a crisis, so
    # the US is worse at distinguishing them.
    secret_decoy_ratio: float = 0
        
    # Files containing external data.
    strategies_filename: str = 'data/tel_strategies.csv'
    bases_filename: str = 'data/tel_bases.csv'

@dataclass
class LowAlert(DefaultConfig):
    mating_fraction: float = 1/6
    roam_fraction: float = .25
    max_roam_duration: timedelta = timedelta(hours=8)
    tel_speed_kmph: float = 20
    emcon_fraction: float = 0
    decoy_ratio: float = 0
    secret_decoy_ratio: float = 0
        
@dataclass
class MediumAlert(DefaultConfig):
    mating_fraction: float = .5
    roam_fraction: float = .75
    max_roam_duration: timedelta = timedelta(hours=16)
    tel_speed_kmph: float = 40
    emcon_fraction: float = .5
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 0

@dataclass
class HighAlert(DefaultConfig):
    mating_fraction: float = 1
    roam_fraction: float = 1
    max_roam_duration: timedelta = timedelta(hours=20)
    tel_speed_kmph: float = 69
    emcon_fraction: float = 1
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 1
        
tel_kinds_continental_us = frozenset({TELKind.DF_31A, TELKind.DF_31AG})
tel_kinds_alaska_hawaii = tel_kinds_continental_us | frozenset({TELKind.DF_31})
tel_kinds_guam = tel_kinds_alaska_hawaii | frozenset({TELKind.DF_26})
tel_kinds_us_allies = tel_kinds_guam | frozenset({TELKind.DF_21AE})