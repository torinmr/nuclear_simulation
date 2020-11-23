from collections import Counter
import csv

from lib.enums import TELState, TELType
from lib.location import Location
from lib.tel import TEL
from lib.tel_strategy import load_strategy

class TELBase:
    """A home base out of which several TELs are stationed."""
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.tels = []
        
    def add_tel(self, **kwargs):
        """Construct a TEL and add it to this base.
        Forwards all keyword args to the TEL constructor."""
        self.tels.append(TEL(self, **kwargs))
        
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

def load_base(row, strategy):
    name = row['name']
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    
    base = TELBase(name, Location(lat, lon))
    for tel_type in TELType:
        if tel_type.name not in row:
            print("No column for {} in TEL base csv file".format(tel_type.name))
            continue

        num_tels = int(row[tel_type.name])
        for _ in range(num_tels):
            base.add_tel(tel_type=tel_type, strategy=strategy)
    return base

def load_bases(base_filename=None, strategy_filename=None):
    strategy = load_strategy(strategy_filename)
    with open(base_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        return [load_base(row, strategy) for row in reader]
    