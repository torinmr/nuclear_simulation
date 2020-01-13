from lib.entity import Entity
from lib.interceptor_system import InterceptorSystem
from lib.location import Location

class AircraftPatrolGroup(Entity):
    """
    Simulates a group of aircraft that collectively provide for one aircraft always in
    patrol around a specific spot.
    """
    def __init__(self, s, name, location, system="F-15J/DJ"):        
        Entity.__init__(self, s, name, location)
        s.aircraft.append(self)

        self.system = system
        self.reloads = 1 # 5 planes -> 1 CAP plane-equivalent
        self.reload_time = 60*60*12  # 2 sorties / day. 
                                     # TODO: determine dynamically, according to nearest surviving airbase.       
 
        # setup - F-15J/DJ
        if self.system == "F-15J/DJ":
            
            # aircraft's own speed, unrefueled combat radius
            self.speed = 0.8575 # km / s
            self.range = 1967 # km
            
            # Area the aircraft can fly to to intercept a missile.
            # We expand the interceptors' range by this amount to roughly approximate
            # the fact that aircraft can effectively expand their range by flying
            # towards the missile.
            patrol_range = self.speed * 120
            
            # 4x AIM-9J/L Sidewinder
            self.aim9_interceptors = InterceptorSystem(
                'AIM-9J/L', self, 0.8575, 28.9682 + patrol_range, 4, 60*60, self.reloads)
            
            # 4x AIM-7E/F Sparrow
            self.aim7_interceptors = InterceptorSystem(
                'AIM-7E/F', self, 1.372, 70.376 + patrol_range, 4, 60*60, self.reloads)
        
        # setup - F-2A
        if self.system == "F-2A/B":
            
            # aircraft's own speed, unrefueled combat radius
            self.speed = 0.686 # km / s
            self.range = 843 # km
            
            patrol_range = self.speed * 120

            # 1x AIM-9J/L Sidewinder
            self.aim9_interceptors = InterceptorSystem(
                'AIM-9J/L', self, 0.8575, 28.9682 + patrol_range, 1, 60*60, self.reloads)
            
            # 1x AIM-7E/F Sparrow
            self.aim7_interceptors = InterceptorSystem(
                'AIM-7E/F', self, 1.372, 70.376 + patrol_range, 1, 60*60, self.reloads)
            
        # F-4EJ
        if self.system == "F-4EJ":
            
            # aircraft's own speed, unrefueled combat radius
            self.speed = 0.7648899104 # km / s
            self.range = 680 # km
            
            patrol_range = self.speed * 120

            # 4x AIM-9J/L Sidewinder
            self.aim9_interceptors = InterceptorSystem(
                'AIM-9J/L', self, 0.8575, 28.9682 + patrol_range, 4, 60*60, self.reloads)
            
            # 4x AIM-7E/F Sparrow
            self.aim7_interceptors = InterceptorSystem(
                'AIM-7E/F', self, 1.372, 70.376 + patrol_range, 4, 60*60, self.reloads)       
            
        # F-35A
        if self.system == "F-35A":
 
            # aircraft's own speed, unrefueled combat radius
            self.speed = 0.55223 # km / s
            self.range = 1407 # km
            
            patrol_range = self.speed * 120
            
            # 14x AIM-120 AMRAAM
            self.aim120_interceptors = InterceptorSystem(
                'AIM-120 AMRAAM', self, 1.372, 160.0 + patrol_range, 14, 60*60, self.reloads)
                
            # 2x AIM-9J/L Sidewinder
            self.aim9_interceptors = InterceptorSystem(
                'AIM-9J/L', self, 0.8575, 28.9682 + patrol_range, 2, 60*60, self.reloads)

    # determine whether to fire interceptor
    def maybe_launch_interceptor(self, time, missile):
        
        # shoot missiles iff midflight, cruise, alive
        if missile.state != 'midflight':
            return
        
        if missile.kind != 'cruise':
            return

        # I assume they want to use the best weapons systems first.
        if hasattr(self, 'aim120_interceptors'):
            self.aim120_interceptors.maybe_launch_interceptor(time, missile)
        if hasattr(self, 'aim7_interceptors'):
            self.aim7_interceptors.maybe_launch_interceptor(time, missile)
        if hasattr(self, 'aim9_interceptors'):
            self.aim9_interceptors.maybe_launch_interceptor(time, missile)
        
    def status_string(self):
        status = 'Aircraft Patrol Group ({}) {}.'.format(self.system, Entity.status_string(self))
        if hasattr(self, 'aim9_interceptors'):
            status += '\n  AIM-9J/L Sidewinder: {}'.format(
                self.aim9_interceptors.status_string())
        if hasattr(self, 'aim7_interceptors'):
            status += '\n  AIM-7E/F Sparrow: {}'.format(
                self.aim7_interceptors.status_string())
        if hasattr(self, 'aim120_interceptors'):
            status += '\n  AIM-120 AMRAAM: {}'.format(
                self.aim120_interceptors.status_string())
        return status