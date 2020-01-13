from lib.entity import Entity

class Airbase(Entity):
    """
    What: Airbases!
    Role: They house and reload aircraft, which provide cruise missile defense.
    """
    def __init__(self, s, name, location):
        Entity.__init__(self, s, name, location)
        s.airbases.append(self)
        
        self.num_missile_hits = 0
        self.state = 'operational'

    def resolve_missile_impact(self, kind):
        if kind == 'cruise':
            self.num_missile_hits += 1
        elif kind == 'ballistic':
            self.num_missile_hits += 3
        
        # TODO: Actually model destruction of runways
        # and aircraft, as per RAND methodology. This
        # is important because airbase size differs
        # significantly, so our blanket estimate here is
        # probably fairly off.
        if self.num_missile_hits >= 30: 
            self.state = 'destroyed'
        
    def status_string(self):
        return 'Airbase {}. State: {}. Num hits: {}'.format(
            Entity.status_string(self), self.state, self.num_missile_hits)