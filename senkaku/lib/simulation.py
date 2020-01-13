from heapq import heappop, heappush

from lib.aegis_ashore import AegisAshore
from lib.airbase import Airbase
from lib.aircraft import AircraftPatrolGroup
from lib.launcher import Launcher
from lib.location import Location
from lib.missile import Missile
from lib.port import Port
from lib.radar import Radar
from lib.renderer import Renderer
from lib.sam import SAM
from lib.ship import Ship

class Simulation:
    def __init__(self):
        self.event_queue = []

        self.aegis_ashores = []
        self.airbases = []
        self.aircraft = []
        self.launchers = []
        self.missiles = []
        self.ports = []
        self.radars = []
        self.sams = []
        self.ships = []
        
        self.last_event_time = -1
        self.next_event_id = 0
        self.missile_tracking_enabled = False
        
        # We begin the missile position updating loop.
        self.schedule_event(self.last_event_time + 1, self.update_missile_locations)

    def set_render_times(self, render_times, save_folder):
        self.renderer = Renderer(self, save_folder)
        self.num_renders_written = 0
        self.render_times = render_times   
        
    def get_all_entities(self):
        return (self.aegis_ashores + self.airbases + self.aircraft + self.launchers
                + self.missiles + self.ports + self.radars + self.sams + self.ships)
        
    def process_next_event(self):
        """Pop the next event off of the queue and resolve it.
        
        Returns:
          True iff an event was processed.
        """
        if len(self.event_queue) > 0:
            time, _, func = heappop(self.event_queue)
            if self.last_event_time != time:
                if len(self.render_times) > self.num_renders_written:
                    render_time = self.render_times[self.num_renders_written]
                    if time >= render_time:
                        self.num_renders_written += 1
                        name = 'render_{}'.format(render_time)
                        print('Rendering {}.'.format(name))
                        self.renderer.render(name)
                        print('Render complete.')
                if time % 100 == 0:
                    print('{}: Simulation ongoing.'.format(time))
                    
            func(time)
            
            self.last_event_time = time
            return True
        else:
            return False

    def schedule_event(self, time, event):
        """Schedule an event for future execution.
        
        Args:
          time: An integer encoding the number of seconds since
                the start of the scenario.
          event: A lambda that takes the time the event happens
                 as an argument, and resolves the effects of the
                 event (including enqueuing any future events).
        """
        # We add an "event id" field to handle events which happen at
        # the same time. This is just an ever-increasing integer, so it
        # ensures that events happening at the same time step happen in
        # the order they were enqueued.
        heappush(self.event_queue, (time, self.next_event_id, event))
        self.next_event_id += 1      

    def enable_missile_tracking(self, time):
        """Tell the simulation to start tracking the locations of missiles.
        
        This is kind of expensive, so we save a lot by not doing it when
        there are no missiles in flight.
        """
        if not self.missile_tracking_enabled:
            self.missile_tracking_enabled = True
            self.schedule_event(time + 1, self.update_missile_locations)
    
    def update_missile_locations(self, time):
        """Update missile locations, and give interceptors a chance to shoot at them."""
        missile_updated = False
        for m in self.missiles:
            if m.state != 'midflight':
                continue

            missile_updated = True
            m.location = m.location.move_towards(m.target.location, m.speed)

            for aa in self.aegis_ashores:
                aa.maybe_launch_interceptor(time, m)
            for ac in self.aircraft:
                ac.maybe_launch_interceptor(time, m)
            for sam in self.sams:
                sam.maybe_launch_interceptor(time, m)
            for sh in self.ships:
                sh.maybe_launch_interceptor(time, m)    

        if self.event_queue and missile_updated:
            self.schedule_event(time + 1, self.update_missile_locations)

        if not missile_updated:
            self.missile_tracking_enabled = False

    def load_csv_lines_from_file(self, filename):
        f = open(filename)
        _ = f.readline()  # Throw the first line away
        while True:
            line = f.readline()
            # Get rid of trailing newlines
            if line[-1:] == '\n':
                line = line[:-1]
            if not line:
                break
            yield line.split(',')
        f.close()
    
    def load_entities_from_files(self, filename_dict):
        if 'aegis_ashore' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['aegis_ashore']):
                name, lat, lon, bmd, cmd = line
                AegisAshore(self, name, Location(lat, lon), bmd, cmd)
        if 'airbase' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['airbase']):
                name, lat, lon = line
                Airbase(self, name, Location(lat, lon))
        if 'aircraft' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['aircraft']):
                name, lat, lon, system = line
                AircraftPatrolGroup(self, name, Location(lat, lon), system)
        if 'launcher' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['launcher']):
                name, lat, lon, kind, system = line
                Launcher(self, name, Location(lat, lon), kind.lower(), system)
        if 'port' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['port']):
                name, lat, lon = line
                Port(self, name, Location(lat, lon))
        if 'radar' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['radar']):
                name, lat, lon = line
                Radar(self, name, Location(lat, lon))
        if 'sam' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['sam']):
                name, lat, lon, system, max_interceptors = line
                SAM(self, name, Location(lat, lon), system, max_interceptors)
        if 'ship' in filename_dict:
            for line in self.load_csv_lines_from_file(filename_dict['ship']):
                name, lat, lon, shiptype = line
                Ship(self, name, Location(lat, lon), shiptype)

    def print_state(self):
        print()
        if len(self.event_queue) > 0:
            next_event_time = self.event_queue[0][0]
        else:
            next_event_time = self.last_event_time + 1

        print("********************************************************")
        print("Simulation state between time {} and {}:".format(self.last_event_time, next_event_time))
        print()
        
        for aegis_ashore in self.aegis_ashores:
            print(aegis_ashore.status_string())
        print()
        
        for airbase in self.airbases:
            print(airbase.status_string())
        print()
        
        aircraft_system_count = {}
        for aircraft in self.aircraft:
            if aircraft.system not in aircraft_system_count:
                aircraft_system_count[aircraft.system] = 0
            aircraft_system_count[aircraft.system] += 1
        for system, count in aircraft_system_count.items():
            print('{} {} aircraft patrol groups'.format(count, system))
        print()
        
        launcher_system_count = {}
        for launcher in self.launchers:
            if launcher.system not in launcher_system_count:
                launcher_system_count[launcher.system] = 0
            launcher_system_count[launcher.system] += 1
        for system, count in launcher_system_count.items():
            print('{} {} launchers'.format(count, system))
        print()
        
        ballistic_missile_state_count = {}
        cruise_missile_state_count = {}
        for missile in self.missiles:
            if missile.kind == 'ballistic':
                state_count = ballistic_missile_state_count
            else:
                state_count = cruise_missile_state_count
            if missile.state not in state_count:
                state_count[missile.state] = 0
            state_count[missile.state] += 1
        for state, count in ballistic_missile_state_count.items():
            print('{} {} ballistic missiles'.format(count, state))
        for state, count in cruise_missile_state_count.items():
            print('{} {} cruise missiles'.format(count, state))
        print()
        
        for port in self.ports:
            print(port.status_string())
        print()
        
        for radar in self.radars:
            print(radar.status_string())
        print()
        
        for sam in self.sams:
            print(sam.status_string())
        print()
        
        for ship in self.ships:
            print(ship.status_string())    
        print()
        
        print("********************************************************")
        print()
        