from collections import Counter

from lib.enums import TELState

class TELBase:
    """A home base out of which several TELs are stationed."""
    def __init__(self, s, name, location):
        self.s = s
        self.name = name
        self.location = location
        self.tels = []
    
    def status(self):
        return '{} TEL Base ({} TELs) {}'.format(
            self.name, len(self.tels), self.location.to_string())
    
    def tel_state_summary(self):
        state_counts = Counter()
        for tel in self.tels:
            state_counts[tel.state] += 1
            
        s = ''
        for state in TELState:
            s += '{} TELs in state {}\n'.format(state_counts[state], state.name)
        return s
