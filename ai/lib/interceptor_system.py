import random
from lib.util import can_intercept

class InterceptorSystem:
    def __init__(self, name, carrier, speed, max_range, max_interceptors, reload_time, reloads):
        self.name = '{} {}'.format(carrier.name, name)
        self.carrier = carrier # The enclosure (ship, SAM, etc.) for this system.
        self.speed = float(speed)
        self.max_range = float(max_range)
        self.max_interceptors = int(max_interceptors)
        self.interceptors = int(max_interceptors)
        self.reload_time = float(reload_time)
        self.reloads = float(reloads)
        self.state = 'operational'
    
    def maybe_launch_interceptor(self, time, missile):

        # TODO: assess: is shoot-look-shoot possible 
        # across all missile defenses, or is this it?
            ##### INSERT: FANCY CODE AND/OR MATH ######
        # if: some stuff
        shoot_look_shoot = missile.kind == 'cruise'

        # if SLS is possible
        if shoot_look_shoot == True:
            if missile.interceptors < 1:
                self._launch_interceptor(time, missile)
        
        # if SLS isn't possible
        if shoot_look_shoot == False:
            while missile.interceptors < 2:
                interceptor_launched = self._launch_interceptor(time, missile)
                if not interceptor_launched:
                    break # Launching failed, don't keep trying.
        
    # after launch: manage interceptor count, schedule interception, reload/exhaust
    def _launch_interceptor(self, time, missile):
        """This function is private because it begins with an underscore,
           meaning it shouldn't be called from outside of this module. Should
           only be called by maybe_launch_interceptor.
           
           Returns: True iff an interceptor was launched.
           """
        if self.state != 'operational':
            return False
        
        intercept_time = can_intercept(
                missile, self.carrier.location, self.speed, self.max_range)
        if not intercept_time:
            return False
        
        # manage interceptor count
        assert(self.interceptors > 0)
        self.interceptors -= 1
        missile.interceptors += 1
        
        # schedule interception
        self.carrier.s.schedule_event(time + intercept_time,
                                      lambda t, self=self, missile=missile:
                                      self.intercept(t, missile))
        print('{}: {} launching interceptor towards {} missile. Distance {} km.'.format(
            time, self.name, missile.kind,
            self.carrier.location.distance_to(missile.location)))
    
        # reload or exhaust
        if self.interceptors == 0:
            if self.reloads > 0:
                self.state = 'reloading'
                self.reloads -= 1
                print('{}: {} interceptor reloading.'.format(time, self.name))
                self.carrier.s.schedule_event(time + self.reload_time,
                                              lambda t, self=self:
                                              self.finish_reload(t))
            else:
                self.state = 'exhausted'
                print('{}: {} reloads exhausted'.format(time, self.name))
        
        return True
    
    def intercept(self, time, missile):
        missile.interceptors -= 1
        
        # check if missile is destroyed
        if missile.state != 'midflight':
            print('{}: {} missile no-longer in flight, {} interceptor wasted.'.format(
                time, missile.kind, self.name))
            return
        
        # check for functioning radar w/in 370 km
        intercept_prob = 0.2 # w/o radar
        for r in self.carrier.s.radars:
            if r.state == 'operational':
                if missile.location.distance_to(r.location) <= 370:
                    intercept_prob = 0.7 # w/radar
    
        # calculate if missile is killed
        if random.random() < intercept_prob:
            missile.state = 'destroyed'
            print('{}: {} interceptor destroyed {} missile. Distance {} km.'.format(
                time, self.name, missile.kind,
                self.carrier.location.distance_to(missile.location)))
        else:
            print('{}: {} interceptor missed {} missile. Distance {} km.'.format(
                time, self.name, missile.kind,
                self.carrier.location.distance_to(missile.location)))
        
    def finish_reload(self, time):
        self.state = 'operational'
        self.interceptors = self.max_interceptors
        print('{}: {} reload completed, {} interceptors available.'.format(
            time, self.name, self.interceptors))
        
    def status_string(self):
        return '{}: State: {}. {}/{} interceptors.'.format(
            self.name, self.state, self.interceptors, self.max_interceptors)