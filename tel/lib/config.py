from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional, FrozenSet, List, Tuple, Dict

from lib.enums import TELKind, TELState, TLOKind

@dataclass
class DefaultConfig:
    # TEL kinds relevant to the simulation. If provided, TEL kinds not on the
    # list are not simulated and not tracked by the US.
    tel_kinds: Optional[FrozenSet[TELKind]] = None
        
    # Fraction of TELs mated (armed with a nuclear warhead) at any given time.
    mating_fraction: float = 1
        
    # Schedule that each TEL will independently repeat in a loop (at staggered intervals).
    tel_schedule: Tuple[Tuple[timedelta, TELState], ...] = ()
        
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
    
    # Assume each truck drives ~40 hours/week, or ~6 hours/day. We'll assume that 1/3 of driving occurs at
    # night, and the remaining 2/3 during the day, and that both night and day are equally long. So, each
    # truck drives 2/12 nighttime hours and 4/12 daytime hours on average.
    daytime_truck_utilization: float = 1/3
    nighttime_truck_utilization: float = 1/6
        
    # Files containing external data.
    bases_filename: str = 'data/tel_bases.csv'
        
    # How long passes between the weather changes. Per Jones, P. A. (1992) (https://doi.org/10.1175/1520-0450(1992)031%3C0732:CCDAC%3E2.0.CO;2)
    # Figure 5, cloud cover is significantly temporally decorrelated after 6-12 hours.
    weather_change_frequency: timedelta = timedelta(hours=6)
        
    # Probability of seeing a TEL at a given moment in time when it's cloudy.
    cloudy_visibility: float = 0.5
        
    # TODO: Should this be switched to a per-base value?
    total_eo_tiles: int = 20_000_000
        
    # How many minutes pass between SAR passes of a particular region of China.
    sar_cadence_min: int = 60
        
    # TODO: Make this not a wild guess.
    per_base_sar_tiles: int = 2_000_000
    
    # Chances that an image will be classified as a TEL by an ML algorithm or a human, respectively.
    # Defined for each kind of TLO, so it represents either a true positive or a false positive rate
    # depending on the kind.
    ml_positive_rates: Dict[TLOKind, float] = field(default_factory=lambda: {
        TLOKind.TEL:   .95,
        TLOKind.TRUCK: .01,
        TLOKind.DECOY: .95,
        TLOKind.SECRET_DECOY: .95,
    })
    ml_non_tlo_positive_rate: float = .001
    ml_processing_duration: timedelta = timedelta(minutes=5)

    human_positive_rates: Dict[TLOKind, float] = field(default_factory=lambda: {
        TLOKind.TEL:   .95,
        TLOKind.TRUCK: .1,
        TLOKind.DECOY: .95*.5,
        TLOKind.SECRET_DECOY: .95*.9,
    })
    human_examples_per_minute: float = 7800
    
@dataclass
class LowAlert(DefaultConfig):
    mating_fraction: float = 1/6
    tel_schedule: Tuple[Tuple[timedelta, TELState], ...] = (
        # 8 hours roaming, 32 hours in base. 25% roaming time overall.
        (timedelta(hours=23), TELState.IN_BASE),
        (timedelta(minutes=30), TELState.LEAVING_BASE),
        (timedelta(hours=8), TELState.ROAMING),
        (timedelta(minutes=30), TELState.ARRIVING_BASE),
    )
    tel_speed_kmph: float = 20
    emcon_fraction: float = 0
    decoy_ratio: float = 0
    secret_decoy_ratio: float = 0
        
@dataclass
class MediumAlert(DefaultConfig):
    mating_fraction: float = .5
    tel_schedule: Tuple[Tuple[timedelta, TELState], ...] = (
        # 16 hours roaming, 5 hours 20 minutes in base. 75% roaming time overall.
        (timedelta(hours=4, minutes=20), TELState.IN_BASE),
        (timedelta(minutes=30), TELState.LEAVING_BASE),
        (timedelta(hours=16), TELState.ROAMING),
        (timedelta(minutes=30), TELState.ARRIVING_BASE),
    )
    tel_speed_kmph: float = 40
    emcon_fraction: float = .5
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 0

@dataclass
class HighAlert(DefaultConfig):
    mating_fraction: float = 1
    tel_schedule: Tuple[Tuple[timedelta, TELState], ...] = (
        # 20 hours/day of driving (including one mid-day refueling stop), 4 hours/day sheltering.
        (timedelta(hours=9, minutes=45), TELState.ROAMING),
        (timedelta(minutes=30), TELState.REFUELING),
        (timedelta(hours=9, minutes=45), TELState.ROAMING),
        (timedelta(hours=4), TELState.SHELTERING),
    )
    tel_speed_kmph: float = 69
    emcon_fraction: float = 1
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 1
        
tel_kinds_continental_us = frozenset({TELKind.DF_31A, TELKind.DF_31AG})
tel_kinds_alaska_hawaii = tel_kinds_continental_us | frozenset({TELKind.DF_31})
tel_kinds_guam = tel_kinds_alaska_hawaii | frozenset({TELKind.DF_26})
tel_kinds_us_allies = tel_kinds_guam | frozenset({TELKind.DF_21AE})