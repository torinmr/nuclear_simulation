from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
import math
from typing import Optional, FrozenSet, List, Tuple, Dict

from lib.enums import TELKind, TELState, TLOKind, Weather, SimulationMode, NukeType

tel_kinds_continental_us = frozenset({TELKind.DF_31A, TELKind.DF_31AG})
tel_kinds_alaska_hawaii = tel_kinds_continental_us | frozenset({TELKind.DF_31})
tel_kinds_guam = tel_kinds_alaska_hawaii | frozenset({TELKind.DF_26})
tel_kinds_us_allies = tel_kinds_guam | frozenset({TELKind.DF_21AE})

@dataclass
class DefaultConfig:
    # Print out verbose debugging information.
    debug: bool = False
    
    # TEL kinds relevant to the simulation. If provided, TEL kinds not on the
    # list are not simulated and not tracked by the US.
    tel_kinds: Optional[FrozenSet[TELKind]] = tel_kinds_alaska_hawaii
        
    # Fraction of TELs mated (armed with a nuclear warhead) at any given time.
    mating_fraction: float = 1
        
    # Schedule that each TEL will independently repeat in a loop (at staggered intervals).
    tel_schedule: Tuple[Tuple[timedelta, TELState], ...] = ()
        
    # TEL speed (in km/h).
    tel_speed_kmph: float = 0
        
    # Maximum distance away from base a TEL can travel. For TELs that return to base at the end of each roam,
    # Actual roam distance is the lesser of this/2 and tel_speed_kmph*roam_time/2.
    tel_max_range_km: float = 0
    
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
        
    output_dir: str = 'output/test'
        
    # How long passes between the weather changes. Per Jones, P. A. (1992) (https://doi.org/10.1175/1520-0450(1992)031%3C0732:CCDAC%3E2.0.CO;2)
    # Figure 5, cloud cover is significantly temporally decorrelated after 6-12 hours.
    weather_change_frequency: timedelta = timedelta(hours=6)

    weather_probabilities: Dict[Weather, float] = field(default_factory=lambda: {
        Weather.CLEAR: .3,
        Weather.CLOUDY: .35,
        Weather.OVERCAST: .35,
    })
    # Probability of observing a TEL with EO at a given moment in time when it's cloudy.
    cloudy_visibility: float = 0.5
   
    # Total area of China.
    area_of_china_km2: int = 9_388_250
    population_of_china: int = 1_394_000_000
        
    # Percentage of China's area that is observable from within 400km of the coast.
    # Rough guesstimate. Only used in free roaming mode, otherwise base-local data is used.
    offshore_observability: float = .3
    # How often to update whether a free-roaming TEL is near the shore or not.
    offshore_change_frequency: timedelta = timedelta(hours=4)

    # How many 250m x 250m tiles need to be examined per km2 of land area.
    # Would be naively be 16, but is adjusted downward based on the density of roads in China.
    # China has around .52 km of road per km2 of area and 4 tiles can cover one km of road, so
    # about 2.1 satellite tiles per km2 are needed on average.
    satellite_tiles_per_road_km: float = 4
    road_km_per_km2: float = .5221
        
    # Total count of (heavy) trucks in China.
    trucks_in_china: int = 1_115_000
        
    simulation_mode: SimulationMode = SimulationMode.BASE_LOCAL
        
    # How many minutes pass between SAR passes of a particular region of China.
    # Includes overhead time, so cadency=30 duration=5 means 25 minutes off, 5 minutes on.
    sar_cadence_min: int = 30
    # How long each SAR pass lasts (maintains visibility of a given point).
    sar_duration_min: int = 5
        
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
        
    # Probability (once per hour indendently for each TEL) to detect a TEL not practicing emissions control.
    sigint_hourly_detect_chance: float = 0.05
    
    # Probability a ground sensor monitoring entrances and exits of TEL bases will detect this TLO type.
    ground_sensor_positive_rates: Dict[TLOKind, float] = field(default_factory=lambda: {
        TLOKind.TEL:   .5,
        TLOKind.DECOY: .1,
        TLOKind.SECRET_DECOY: .25,
    })
        
    # Adjustment from km2 occupied by TEL (ignoring roads) to km2 destroyed by nukes.
    # Could be higher than 1 if nukes overlap inefficiently, or less because TELs can only drive
    # on roads.
    destruction_area_factor: float = .5
        
    # Description of US nuclear arsenal. Also determines order of using missiles - earlier missiles
    # are used first (against the "easiest" targets).
    arsenal: Tuple[NukeType, ...] = (
        NukeType('Pacific W76-1', timedelta(minutes=12.4), 405, 31.2),
        NukeType('Pacific W88', timedelta(minutes=12.4), 135, 91.9),  
        NukeType('Distant W76-1', timedelta(minutes=24.8), 270, 31.2),
        NukeType('Distant W88', timedelta(minutes=24.8), 90, 91.9),
        NukeType('W78', timedelta(minutes=30), 120, 74.9),
        NukeType('W87', timedelta(minutes=30), 60, 69.6),
    )
        
    # How many nukes the US launches at each TEL to ensure destruction.
    nukes_per_tel: int = 2
        
    # US missile defense statistics
    num_interceptors: int = 44
    interceptor_kill_prob: float = .5
        
    # Increase China's number of TELs by this ratio.
    tel_count_multiplier: float = 1
        
    def __post_init__(self):
        satellite_tiles_per_km2 = self.road_km_per_km2 * self.satellite_tiles_per_road_km
        
        if self.simulation_mode == SimulationMode.BASE_LOCAL:
            # Max roaming time of a TEL based on its schedule.
            self.max_roam_time = timedelta()
            for (duration, state) in self.tel_schedule:
                if state == TELState.ROAMING and duration > self.max_roam_time:
                    self.max_roam_time = duration

            # How far TELs can travel from base and the area they can cover, assuming they must return
            # afterwards.
            self.tel_radius_km = min(self.tel_speed_kmph * (self.max_roam_time / timedelta(hours=1)) / 2,
                                     self.tel_max_roam_km / 2)
            self.tel_area_km2 = math.pi * self.tel_radius_km**2

            self.satellite_tiles_per_base = self.tel_area_km2 * satellite_tiles_per_km2

            # Number of heavy trucks per person on average.
            self.trucks_per_person = self.trucks_in_china / self.population_of_china

        elif self.simulation_mode == SimulationMode.FREE_ROAMING:
            self.satellite_tiles = satellite_tiles_per_km2 * self.area_of_china_km2
        
        # Percentage of time a given location is visible from SAR satellites.
        self.sar_uptime = self.sar_duration_min / self.sar_cadence_min
    
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
    tel_max_roam_km: float = 250
    simulation_mode: SimulationMode = SimulationMode.BASE_LOCAL
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
    tel_max_roam_km: float = 750
    simulation_mode: SimulationMode = SimulationMode.BASE_LOCAL
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
    simulation_mode: SimulationMode = SimulationMode.FREE_ROAMING
    emcon_fraction: float = 1
    decoy_ratio: float = 1
    secret_decoy_ratio: float = 1

# Configurations to use for tests:
base_configs = {
    'low': LowAlert,
    'med': MediumAlert,
    'high': HighAlert,
}

test_configs = []
for alert_level, C in base_configs.items():
    test_configs.append(C(output_dir='output/normal_{}'.format(alert_level)))
    test_configs.append(C(output_dir='output/full_sar_{}'.format(alert_level),
                          sar_duration_min=30))
    test_configs.append(C(output_dir='output/no_ai_{}'.format(alert_level),
                          ml_positive_rates={
                              TLOKind.TEL:   1,
                              TLOKind.TRUCK: 1,
                              TLOKind.DECOY: 1,
                              TLOKind.SECRET_DECOY: 1,
                          },
                          ml_non_tlo_positive_rate=1,
                          ml_processing_duration=timedelta()))
    test_configs.append(C(output_dir='output/double_tels_{}'.format(alert_level),
                          tel_count_multiplier=2))