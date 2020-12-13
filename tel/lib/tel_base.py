from collections import Counter
import csv

from lib.enums import TELState, TELKind, TLOKind
from lib.intelligence_types import TLO
from lib.location import Location
from lib.tel import TEL

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
        
    def add_tel(self, c, **kwargs):
        """Construct a TEL and add it to this base.
        Forwards all keyword args to the TEL constructor.
        
        Returns: The TEL which was added.
        """
        tel_kind = kwargs["tel_kind"]
        tlo_kind = kwargs["tlo_kind"]
        name = '{}_{}_{}_{}'.format(self.name, tlo_kind.name, tel_kind.name,
                                    self.tel_count_by_kind[(tlo_kind, tel_kind)])
        tel = TEL(c, self, name, **kwargs)
        
        self.tel_count_by_kind[(tlo_kind, tel_kind)] += 1
        self.tels.append(tel)
        return tel
        
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

def load_base(c, row):
    name = row['name']
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    cloud_cover = float(row['cloud_cover'])
    
    base = TELBase(name, Location(lat, lon), cloud_cover=cloud_cover)
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

    trucks = TLO(TLOKind.TRUCK, base=base, multiplicity=int(row['trucks']))
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
    