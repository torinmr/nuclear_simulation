from datetime import datetime, timedelta
from dateutil import tz
from enum import Enum, auto
from heapq import heappop, heappush
from numpy import random

from lib.enums import AlertLevel
from lib.intelligence import Intelligence
from lib.renderer import Renderer
from lib.tel_base import TELBase, load_bases

TZ = tz.gettz('Asia/Shanghai')

class Simulation:
    def __init__(self,
                 start_datetime=datetime.fromisoformat('2021-01-20T12:00:00'),
                 runtime=None,
                 render_interval_mins=60,
                 output_folder='',
                 rng_seed=None,
                 alert_level=AlertLevel.PEACETIME,
                 use_decoys=False,
                 allowed_tel_kinds=None,
                ):
        """Initialize the simulation.
        start_datetime: datetime object representing when the simulation starts.
          No timezone should be specified (assumed to be local time in China).
        runtime: timedelta indicating the maximum amount of time the simulation
          can run for. If not set, the simulation will run forever or until it
          runs out of events.
        render_interval_mins: How frequently to produce a rendering of the
          simulation state, in minutes.
        output_folder: Folder to save renders and other output data. If not provided,
          no data will be saved.
        rng_seed: Optional integer. If provided, use a fixed seed which should make
          the simulation deterministic. If not provided use a random seed.
        alert_level: An AlertLevel enum value.
        use_decoys: Whether to add decoy TLOs based on the 'decoys' column in the base 
          config.
        allowed_tel_kinds: Optional collection of TELKinds. If provided, only add these
          TELs to the simulation, otherwise add all types.
        """
        random.seed(seed=rng_seed)
        self.event_queue = []
        self.t = start_datetime.replace(tzinfo=TZ)
        self.next_event_id = 0
        if runtime:
            self.end_datetime = self.t + runtime
        
        self.render_interval = timedelta(minutes=render_interval_mins)        
        self.renderer = Renderer(output_folder)
        self.alert_level = alert_level
        
        self.bases = load_bases(base_filename='data/tel_bases.csv',
                                strategies_filename='data/tel_strategies.csv')
        self.tel_from_uid = {}
        self.tlo_from_uid = {}
        for base in self.bases:
            for tel in base.tels:
                self.tel_from_uid[tel.uid] = tel
            for tlo in base.tlos:
                self.tlo_from_uid[tlo.uid] = tlo
        
        self.intelligence = Intelligence()
        self.start()
        
    def tels(self):
        return self.tel_from_uid.values()
    
    def tlos(self):
        return self.tlo_from_uid.values()
        
    def start(self):
        """Start each of the entities in the simulation (i.e. schedule their update events)."""
        for base in self.bases:
            base.start(self)
        self.intelligence.start(self)
        self.renderer.start(self)
        
    def run(self):
        """Run the simulation loop until there are no more events, or the max time is reached."""
        while self._process_next_event():
            pass
        self.renderer.render(self)
        self.renderer.final_summary()
    
    def _process_next_event(self):
        """Pop the next event off of the queue and resolve it.
        
        Returns:
          True if the simulation is ongoing, or false if it is over.
        """
        if len(self.event_queue) > 0:
            t, _, func = heappop(self.event_queue)
            if (self.end_datetime and t > self.end_datetime):
                return False
            self.t = t
            func()
            return True
        else:
            return False

    def _schedule_event_at_time(self, event, future_datetime):
        """Schedule an event for future execution.
        
        Args:
          event: A lambda (with no arguments) that resolves the effects of
                 the event (including enqueuing any future events).
          future_datetime: A datetime indicating when the event should
            take place. Not scheduled if it's in the past.
        """
        if future_datetime < self.t:
            print("ERROR: Tried to schedule event in the past.")
            print("  Attempted scheduling time: ", future_datetime)
            print("  Current time: ", self.t)
            return

        # We add an "event id" field to handle events which happen at
        # the same time. This is just an ever-increasing integer, so it
        # ensures that events happening at the same time step happen in
        # the order they were enqueued.
        heappush(self.event_queue, (future_datetime, self.next_event_id, event))
        self.next_event_id += 1
        
    def schedule_event_relative(self, event, delta, repeat_interval=None):
        """Schedule an event to happen at a relative future time
           (e.g. one hour from now).
           
        Args:
          event: A lambda (with no arguments) that resolves the effects of
                 the event (including enqueuing any future events).
          delta: timedelta indicating how far in the future the event should happen.
          repeat_interval: Optional timedelta. If set, repeat the event on this
            interval after the first occurrence.
        """
        if repeat_interval:
            def repeat_event():
                event()
                self.schedule_event_relative(event, repeat_interval,
                                             repeat_interval=repeat_interval)
            self._schedule_event_at_time(repeat_event, self.t + delta)
        else:
            self._schedule_event_at_time(event, self.t + delta)