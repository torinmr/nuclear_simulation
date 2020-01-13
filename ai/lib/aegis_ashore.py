from lib.entity import Entity
from lib.interceptor_system import InterceptorSystem
from lib.location import Location

class AegisAshore(Entity):
    """
    What: Aegis Ashore, an on-shore version of the Aegis system.
    Role: A source of missile defense, as well as a target.
    """
    def __init__(self, s, name, location,
                 bmd='SM-3 Block IIA', # ballistic missile defense 
                 cmd='SM-6',           # cruise missile defense
                 max_interceptors=24,
                 reloads=0):
        Entity.__init__(self, s, name, location)        
        s.aegis_ashores.append(self)

        self.bmd = bmd
        self.cmd = cmd   
        self.state = 'operational'
        self.num_missile_hits = 0

        # setup - ballistic missile defense system
        if bmd == "SM-3 Block IIA":
            self.bmd_interceptor = InterceptorSystem(
                bmd, self, 4.5, 2500, round(max_interceptors*.8),
                24*60*60, reloads)

        # setup - cruise missile defense system
        if cmd == "SM-6":
            self.cmd_interceptor = InterceptorSystem(
                cmd, self, 1.2, 240, round(max_interceptors*.2),
                24*60*60, reloads)
        
    # launch at that exact missile, at this exact moment?
    def maybe_launch_interceptor(self, time, missile):
        # don't shoot destroyed or impacted missiles
        if missile.state != 'midflight':
            return
        
        # are we alive?
        if self.state != 'operational':
            return
        
        # respond to missiles by type
        if missile.kind == 'ballistic':
            self.bmd_interceptor.maybe_launch_interceptor(time, missile)       
        elif missile.kind == 'cruise':
            self.cmd_interceptor.maybe_launch_interceptor(time, missile)

    def resolve_missile_impact(self, kind):
        if kind == 'cruise':
            self.num_missile_hits += 1
        elif kind == 'ballistic':
            self.num_missile_hits += 2
        
        if self.num_missile_hits >= 10: 
            self.state = 'destroyed'
            
    def status_string(self):
        return ('Aegis Ashore {}. State: {}. Num hits: {}.\n'.format(
            Entity.status_string(self), self.state, self.num_missile_hits) +
                '  BMD: {}\n'.format(self.bmd_interceptor.status_string()) +
                '  CMD: {}'.format(self.cmd_interceptor.status_string()))