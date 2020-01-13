from lib.entity import Entity

class Port(Entity):
    """
    What: Ports!
    Role: Ships reload here.
    """
    def __init__(self, s, name, location):
        Entity.__init__(self, s, name, location)
        s.ports.append(self)

        self.num_missile_hits = 0
        self.state = 'operational'
        
    def resolve_missile_impact(self, kind):
        if self.state == 'destroyed':
            return
 
        if kind == 'cruise':
            self.num_missile_hits += 1
        elif kind == 'ballistic':
            self.num_missile_hits += 2
            
        if self.num_missile_hits >= 10:
            print('{} destroyed.'.format(self.name))
            self.state = 'destroyed'
        
    def status_string(self):
        return 'Port {}. State: {}. Num hits: {}'.format(
            Entity.status_string(self), self.state, self.num_missile_hits)