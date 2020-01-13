import copy

from lib.entity import Entity
from lib.location import Location
from lib.missile import Missile

class Launcher(Entity):
    def __init__(self, s, name, location, kind, system):
        Entity.__init__(self, s, name, location)
        s.launchers.append(self)

        self.kind = kind
        self.system = system
        self.reloads = 1
        self.state = 'ready'
        self.missile_speed = 2.7555 # bug-hunting default
        
        # setup - cruise
        if self.kind == 'cruise':
            if self.system == 'DH-10':
                self.missile_speed = 0.2744 # km/s
                
        # setup - ballistic
        if self.kind == 'ballistic':
            if self.system == 'DF-26':
                self.missile_speed = 3.43 # km/s
            if self.system == 'DF-21C':
                self.missile_speed = 3.43 # km/s
            if self.system == 'DF-16':
                self.missile_speed = 2.75 # km/s
            if self.system == 'DF-15B':
                self.missile_speed = 2.058 # km/s
        
        if(self.missile_speed) == 2.7555:
            print("Warning: default missile speed used.")
        
    def launch_missile(self, time, target):
        if self.state != 'ready':
            return
     
        print('{}: {} launching {} missile towards {}.'.format(time, self.name, self.kind, target.name))
        m = Missile(self.s, self.kind, self.location, target, self.missile_speed)
        self.s.enable_missile_tracking(time)
        impact_time = time + self.missile_flight_duration(target)
        self.s.schedule_event(impact_time,
                              lambda t, m=m, target=target:
                              m.missile_impact(t, target))
        
        if self.reloads > 0:
            self.state = 'reloading'
            self.reloads -= 1
            print('{}: {} reloading.'.format(time, self.name))            
            self.s.schedule_event(time + 60*60*60*12, # half a day 
                                  lambda t, self=self, target=target:
                                  self.launch_missile(t, target))
        else:
            self.state = 'exhausted'
            print('{}: {} reloads exhausted'.format(time, self.name))

    def missile_flight_duration(self, target):
        distance_km = self.location.distance_to(target.location)
        if self.kind == 'cruise':
            return int(distance_km / self.missile_speed)
        elif self.kind == 'ballistic':
            return int(distance_km / self.missile_speed)
        else:
            raise ValueError('Invalid kind name {}'.format(kind))
    
    def status_string(self):
        return 'Launcher ({}) {}. State: {}'.format(
            self.kind, Entity.status_string(self), self.state)
