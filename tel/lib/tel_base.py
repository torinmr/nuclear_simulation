from collections import Counter
import csv

from lib.enums import TELState, TELKind, TLOKind
from lib.intelligence_types import TLO
from lib.location import Location
from lib.tel import TEL
from lib.tel_strategy import load_strategies

class TELBase:
    """A home base out of which several TELs are stationed."""
    def __init__(self, name, location, cloud_cover=None):
        self.name = name
        self.location = location
        assert cloud_cover
        self.cloud_cover = cloud_cover
        self.tel_count_by_kind = Counter()
        self.tels = []
        self.tlos = []
        
    def add_tel(self, **kwargs):
        """Construct a TEL and add it to this base.
        Forwards all keyword args to the TEL constructor."""
        tel = TEL(self, 'tmp', **kwargs)
        tel.name = '{}_{}_{}'.format(self.name, tel.kind.name, self.tel_count_by_kind[tel.kind])
        self.tel_count_by_kind[tel.kind] += 1
        self.tels.append(tel)
        self.tlos.append(tel.to_tlo())
        
    def start(self, s):
        for tel in self.tels:
            tel.start(s)
    
    def status(self):
        return '{} TEL Base ({} TELs) {}'.format(
            self.name, len(self.tels), self.location.to_string())
    
    def tel_state_summary(self):
        state_counts = Counter()
        for tel in self.tels:
            state_counts[tel.state] += 1
            
        return '\n'.join(
            ['  {} TELs in state {}'.format(state_counts[state], state.name)
             for state in TELState])

def load_base(row, strategies, decoy_ratio, allowed_tel_kinds):
    name = row['name']
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    cloud_cover = float(row['cloud_cover'])
    
    base = TELBase(name, Location(lat, lon), cloud_cover=cloud_cover)
    for tel_kind in TELKind:
        if allowed_tel_kinds is not None and tel_kind not in allowed_tel_kinds:
            continue
        if tel_kind.name not in row:
            print("No column for {} in TEL base csv file".format(tel_kind.name))
            continue
            
        num_tels = int(row[tel_kind.name])
        for _ in range(num_tels):
            base.add_tel(tel_kind=tel_kind, strategies=strategies)
            
        num_decoys = int(decoy_ratio * num_tels)
        for _ in range(num_decoys):
            base.add_tel(tel_kind=tel_kind, strategies=strategies, is_decoy=True)

    base.tlos.append(TLO(TLOKind.TRUCK, base=base, multiplicity=int(row['trucks']))) 
    return base

def load_bases(base_filename=None, strategies_filename=None,
               decoy_ratio=0, allowed_tel_kinds=None):
    """Args:
      
    """
    strategies = load_strategies(strategies_filename)
    with open(base_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        return [load_base(row, strategies, decoy_ratio, allowed_tel_kinds) for row in reader]
    