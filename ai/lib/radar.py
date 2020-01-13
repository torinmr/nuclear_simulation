from lib.entity import Entity

class Radar(Entity):
    """
    What: Radar detect incoming missiles and aircraft.
    Role: Radar greatly increase interceptor efficacy. 
    """

    def __init__(self, s, name, location):
        Entity.__init__(self, s, name, location)
        s.radars.append(self)

        self.num_missile_hits = 0
        self.state = 'operational'
        self.range = 370 # km
    
    def resolve_missile_impact(self, kind):
        if self.state == 'destroyed':
            return
 
        if kind == 'cruise':
            self.num_missile_hits += 1
        elif kind == 'ballistic':
            self.num_missile_hits += 2

        if self.num_missile_hits >= 3:
            self.state = 'destroyed'
            print('{} destroyed.'.format(self.name))
        
    def status_string(self):
        return 'Radar {}. State: {}. Num hits: {}'.format(
            Entity.status_string(self), self.state, self.num_missile_hits)