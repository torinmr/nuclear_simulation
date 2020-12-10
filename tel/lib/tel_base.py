from collections import Counter
import csv

from lib.enums import TELState, TELType, TLOKind
from lib.intelligence_types import TLO
from lib.location import Location
from lib.tel import TEL
from lib.tel_strategy import load_strategy

class TELBase:
    """A home base out of which several TELs are stationed."""
    def __init__(self, name, location, cloud_cover=None):
        self.name = name
        self.location = location
        assert cloud_cover
        self.cloud_cover = cloud_cover
        self.tel_count_by_type = Counter()
        self.tels = []
        self.tlos = []
        
    def add_tel(self, **kwargs):
        """Construct a TEL and add it to this base.
        Forwards all keyword args to the TEL constructor."""
        tel = TEL(self, 'tmp', **kwargs)
        tel.name = '{}_{}_{}'.format(self.name, tel.type.name, self.tel_count_by_type[tel.type])
        self.tel_count_by_type[tel.type] += 1
        self.tels.append(tel)
        self.tlos.append(TLO(TLOKind.TEL, uid_tel.uid, base=self))
        
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

def load_base(row, strategy, use_decoys, allowed_tel_kinds):
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
            base.add_tel(tel_kind=tel_kind, strategy=strategy)
    
    if use_decoys:
        base.tlos.append(TLO(TLOKind.DECOY, base=base, multiplicity=int(row['decoys'])))
    base.tlos.append(TLO(TLOKind.TRUCK, base=base, multiplicity=int(row['trucks']))) 
    return base

def load_bases(base_filename=None, strategy_filename=None,
               use_decoys=False, allowed_tel_kinds=None):
    """Args:
      
    """
    #
    strategy = load_strategy(strategy_filename)
    with open(base_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        return [load_base(row, strategy, use_decoys, allowed_tel_kinds) for row in reader]
    