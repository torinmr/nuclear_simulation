import random

from lib.entity import Entity
from lib.interceptor_system import InterceptorSystem
from lib.util import can_intercept

class SAM(Entity):
    """
    What: Surface-to-Air Missile batteries, providing static terminal-phase intercept.
    Role: A source of cruise missile defense, as well as a target.
    """
    def __init__(self, s, name, location, system="PAC-3", max_interceptors=32, reloads=1):
        Entity.__init__(self, s, name, location)
        s.sams.append(self)

        self.system = system
        self.state = 'operational'
        self.num_missile_hits = 0
        
        # setup - PAC-3
        if system == "PAC-3":
            self.interceptor = InterceptorSystem(
                system, self, 1.715, 55, max_interceptors, 60*60, reloads)

        # setup - PAC-2 (non-miniaturized)
        if system == "PAC-2":
            self.interceptor = InterceptorSystem(
                system, self, 1.715, 160, max_interceptors, 60*60, reloads)
        
    # launch at that exact missile, at this exact moment?
    def maybe_launch_interceptor(self, time, missile):
        # don't shoot destroyed or impacted missiles
        if missile.state != 'midflight':
            return
                  
        if self.state != 'operational':
            return
        
        self.interceptor.maybe_launch_interceptor(time, missile)
        
    def resolve_missile_impact(self, kind):
        if self.state == 'destroyed':
            return

        if kind == 'cruise':
            self.num_missile_hits += 1
        elif kind == 'ballistic':
            self.num_missile_hits += 3
            
        if self.num_missile_hits >= 5:
            print('{} destroyed.'.format(self.name))
            self.state = 'destroyed'
    
    def status_string(self):
        return ('SAM {}. State: {}. Num hits: {}.\n'.format(
            Entity.status_string(self), self.state, self.num_missile_hits) +
                '  Missile Defense: {}'.format(self.interceptor.status_string()))
