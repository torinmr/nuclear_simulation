import random

from lib.entity import Entity
from lib.interceptor_system import InterceptorSystem
from lib.location import Location

class Ship(Entity):
    """
    What: Ships provide area missile defense.
    Role: Ships are assumed invulnerable for doctrinal & simplifying reasons.
    """
    def __init__(self, s, name, location,
                 shiptype="Atago Class DDG",
                 reloads=0):
        Entity.__init__(self, s, name, location)
        s.ships.append(self)

        self.shiptype = shiptype
        self.reloads = reloads 
        
        # TODO: Dynamically calculate reload time - should be time needed to
        # steam to nearest port and back, plus like half a day for actual reloading.
        
        # TODO: Atago has just the SM-2; Kongo has SM-2 and SM-3. Possibly
        # there's a more elegant way to code this. Another TODO here is that
        # Japan has different amounts of both (way less of the SM-3), so the
        # reload counter should be different for both weapons.
        
        # setup - defined shiptype: Atago DDG
        if self.shiptype == "Atago Class DDG":
            self.sm2_interceptors = InterceptorSystem(
                'SM-2', self, 1.2, 167, 48, 60*60*24*2, reloads)

        # setup - defined shiptype: Kongo DDG
        if self.shiptype == "Kongo Class DDG":
            self.sm2_interceptors = InterceptorSystem(
                'SM-2', self, 1.2, 167, 27, 60*60*24*2, reloads)
                
            self.sm3_interceptors = InterceptorSystem(
                'SM-3', self, 3, 700, 27, 60*60*24*2, reloads)

    # launch at that exact missile, at this exact moment?    
    def maybe_launch_interceptor(self, time, missile):
        
        # don't shoot destroyed or impacted missiles
        if missile.state != 'midflight':
            return          
        
        # respond to missiles by type
        if missile.kind == 'ballistic':
            if self.shiptype == "Kongo Class DDG": # SM-3s can be BMD; SM-2s can't
                self.sm3_interceptors.maybe_launch_interceptor(time, missile)
        
        # so, according to Eric, if we assume ships are invulnerable we should assume
        # they can't intercept any cruise missiles, because it means they're ducking
        # line-of-sight (to avoid being targeted by China, but which they would also
        # need to see / hit cruise missiles). They can still shoot down ballistics
        # because ballistics go high rather than hugging terrain.
        
        # elif missile.kind == 'cruise':   
        #    # SM-2s when available; SM-3s next when available
        #    if self.sm2_interceptors.state != "operational":
        #        if self.shiptype == "Kongo Class DDG":
        #              self.sm3_interceptors.maybe_launch_interceptor(time, missile)        
        #    else:
        #        self.sm2_interceptors.maybe_launch_interceptor(time, missile)
                
    def status_string(self):
        status = 'Ship ({}) {}.'.format(self.shiptype, Entity.status_string(self))
        if hasattr(self, 'sm2_interceptors'):
            status += '\n  SM-2: {}'.format(self.sm2_interceptors.status_string())
        if hasattr(self, 'sm3_interceptors'):
            status += '\n  SM-3: {}'.format(self.sm3_interceptors.status_string())
        return status
