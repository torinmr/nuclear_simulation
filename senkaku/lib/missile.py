from lib.entity import Entity

class Missile(Entity):
    missile_num = 0  # Global count of missiles created.
    
    def __init__(self, s, kind, location, target, speed):
        name = '{}_missile_{}'.format(kind, Missile.missile_num)
        Missile.missile_num += 1
        Entity.__init__(self, s, name, location)
        s.missiles.append(self)
        
        self.state = 'midflight'
        self.kind = kind
        self.target = target
        self.speed = speed
        
        # The number of interceptors currently en-route to this missile.
        self.interceptors = 0
        
        if kind == 'cruise':
            pass
        elif kind == 'ballistic':
            pass
        else:
            raise ValueError("Invalid kind name {}".format(kind))
    
    def missile_impact(self, time, target):
        if self.state != 'midflight':
            return
        
        print('{}: {} missile impact on {}.'.format(time, self.kind, target.name))
        target.resolve_missile_impact(self.kind)
        self.state = 'impacted'
        
    def status_string(self):
        return 'Missile {}. State: {}. Interceptors: {}.'.format(
            Entity.status_string(self), self.state, self.interceptors)
        