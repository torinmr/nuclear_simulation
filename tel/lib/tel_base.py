from collections import Counter
import csv
from datetime import timedelta
import numpy.random as random

from lib.enums import TELState, TELKind, TLOKind, Weather
from lib.intelligence_types import TLO
from lib.location import Location
from lib.tel import TEL

class TELBase:
    """A home base out of which several TELs are stationed."""
    def __init__(self, c, name, location, offshore_observability=0):
        self.c = c
        self.name = name
        self.location = location
        self.tel_count_by_kind = Counter()
        self.tels = []
        self.tlos = []
        self.offshore_observability = offshore_observability    

    def update_weather(self):
        self.weather = Weather(random.choice(list(self.c.weather_probabilities.keys()),
                                             p=list(self.c.weather_probabilities.values())))
        if self.c.debug:
            print("Weather in {} is now {}".format(self.name, self.weather.name))
        
    def add_tel(self, c, baseless=False, **kwargs):
        """Construct a TEL and add it to this base.
        Forwards all keyword args to the TEL constructor.
        
        Args:
          c: Config
          baseless: If true, don't permanently link the TEL to this base.
        
        Returns: The TEL which was added.
        """
        tel_kind = kwargs["tel_kind"]
        tlo_kind = kwargs["tlo_kind"]
        name = '{}_{}_{}_{}'.format(self.name, tlo_kind.name, tel_kind.name,
                                    self.tel_count_by_kind[(tlo_kind, tel_kind)])
        if baseless:
            tel = TEL(c, None, name, **kwargs)
        else:
            tel = TEL(c, self, name, **kwargs)
            self.tels.append(tel)
        
        self.tel_count_by_kind[(tlo_kind, tel_kind)] += 1
        return tel
        
    def start(self, s):
        self.update_weather()
        for tel in self.tels:
            tel.start(s)
            
        frequency = self.c.weather_change_frequency
        offset = timedelta(minutes=random.randint(frequency / timedelta(minutes=1)))
        s.schedule_event_relative(self.update_weather, offset, repeat_interval=frequency)
        
        offset_mins = hash(self.name + "SAR") % self.c.sar_cadence_min
        self.sar_offset = s.t + timedelta(minutes=offset_mins)   
    
    def status(self):
        return '{} TEL Base ({} TELs) {} is {}'.format(
            self.name, len(self.tels), self.location.to_string(), self.weather.name)

    def tel_state_summary(self):
        state_counts = Counter()
        for tel in self.tels:
            state_counts[tel.state] += 1
            
        return '\n'.join(
            ['  {} TELs in state {}'.format(state_counts[state], state.name)
             for state in TELState])

def load_base(c, row):
    name = row['name']
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    offshore_observability = float(row['offshore_observability'])
    persons_per_km2 = float(row['population_density'])
    
    base = TELBase(c, name, Location(lat, lon), offshore_observability=offshore_observability)
    for tel_kind in TELKind:
        if c.tel_kinds is not None and tel_kind not in c.tel_kinds:
            continue
        if tel_kind.name not in row:
            print("No column for {} in TEL base csv file".format(tel_kind.name))
            continue
            
        num_tels = int(row[tel_kind.name])
        for _ in range(num_tels):
            tel = base.add_tel(c, tel_kind=tel_kind, tlo_kind=TLOKind.TEL)
            tlo = TLO(kind=TLOKind.TEL, tel=tel, uid=tel.uid, base=base)
            base.tlos.append(tlo)
            
        num_decoys = int(c.decoy_ratio * num_tels)
        for _ in range(num_decoys):
            tel = base.add_tel(c, tel_kind=tel_kind, tlo_kind=TLOKind.DECOY)
            tlo = TLO(kind=TLOKind.DECOY, tel=tel, uid=tel.uid, base=base)
            base.tlos.append(tlo)
            
        num_secret_decoys = int(c.secret_decoy_ratio * num_tels)
        for _ in range(num_secret_decoys):
            tel = base.add_tel(c, tel_kind=tel_kind, tlo_kind=TLOKind.SECRET_DECOY)
            tlo = TLO(kind=TLOKind.SECRET_DECOY, tel=tel, uid=tel.uid, base=base)
            base.tlos.append(tlo)

    num_trucks = c.trucks_per_person * persons_per_km2 * c.tel_area_km2
    trucks = TLO(TLOKind.TRUCK, base=base, multiplicity=num_trucks)
    base.tlos.append(trucks)
    
    if len(base.tels) > 0:
        return base
    else:
        return None

def load_bases(c):
    with open(c.bases_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        bases = []
        for row in reader:
            base = load_base(c, row)
            if base is not None:
                bases.append(base)
        return bases

def load_tels_from_base(c, row):
    tels = []
    tlos = []
    name = row['name']
    
    # Hack alert: We create base to help with naming and initializing the TELs, and then discard it.
    base = TELBase(c, name, Location(0, 0))
    for tel_kind in TELKind:
        if c.tel_kinds is not None and tel_kind not in c.tel_kinds:
            continue
        if tel_kind.name not in row:
            print("No column for {} in TEL base csv file".format(tel_kind.name))
            continue
            
        num_tels = int(row[tel_kind.name])
        for _ in range(num_tels):
            tel = base.add_tel(c, baseless=True, tel_kind=tel_kind, tlo_kind=TLOKind.TEL)
            tlo = TLO(kind=TLOKind.TEL, tel=tel, uid=tel.uid)
            tels.append(tel)
            tlos.append(tlo)
            
        num_decoys = int(c.decoy_ratio * num_tels)
        for _ in range(num_decoys):
            tel = base.add_tel(c, baseless=True, tel_kind=tel_kind, tlo_kind=TLOKind.DECOY)
            tlo = TLO(kind=TLOKind.DECOY, tel=tel, uid=tel.uid)
            tels.append(tel)
            tlos.append(tlo)
            
        num_secret_decoys = int(c.secret_decoy_ratio * num_tels)
        for _ in range(num_secret_decoys):
            tel = base.add_tel(c, baseless=True, tel_kind=tel_kind, tlo_kind=TLOKind.SECRET_DECOY)
            tlo = TLO(kind=TLOKind.SECRET_DECOY, tel=tel, uid=tel.uid)
            tels.append(tel)
            tlos.append(tlo)
    
    return tels, tlos

def load_tels_from_bases(c):
    with open(c.bases_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        tels = []
        tlos = []
        for row in reader:
            new_tels, new_tlos = load_tels_from_base(c, row)
            tels += new_tels
            tlos += new_tlos

        trucks = TLO(TLOKind.TRUCK, multiplicity=c.trucks_in_china)
        tlos.append(trucks)
        return tels, tlos
    