class TELBase:
    """A home base out of which several TELs are stationed."""
    def __init__(self, s, name, location):
        self.s = s
        self.name = name
        self.location = location
        self.tels = []
    
    def status_string(self):
        return '{} TEL Base ({} TELs) {}'.format(
            self.name, len(self.tels), self.location.to_string())
    
    def is_daylight(self):
        return location.is_daylight(self.s.t)
