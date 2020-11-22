from datetime import datetime, timedelta
from dateutil import tz
from heapq import heappop, heappush

from lib.location import Location
from lib.renderer import Renderer
from lib.tel_base import TELBase

TZ = tz.gettz('Asia/Shanghai')

class Simulation:
    def __init__(self,
                 start_datetime=datetime.fromisoformat('2021-01-20T12:00:00'),
                 runtime=None,
                 render_interval_mins=60,
                 output_folder=''):
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
        """
        self.event_queue = []
        self.t = start_datetime.replace(tzinfo=TZ)
        self.next_event_id = 0
        if runtime:
            self.end_datetime = self.t + runtime
        
        self.render_interval = timedelta(minutes=render_interval_mins)        
        self.renderer = Renderer(self, output_folder)
        
    def run(self):
        self._schedule_event_relative(
            timedelta(), self.renderer.render, self.render_interval)
        while self._process_next_event():
            pass
        self.renderer.render()
    
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

    def _schedule_event_at_time(self, future_datetime, event):
        """Schedule an event for future execution.
        
        Args:
          future_datetime: A datetime indicating when the event should
            take place. Not scheduled if it's in the past.
          event: A lambda (with no arguments) that resolves the effects of
                 the event (including enqueuing any future events).
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
        
    def _schedule_event_relative(self, delta, event, repeat_interval=None):
        """Schedule an event to happen at a relative future time
           (e.g. one hour from now).
           
        Args:
          delta: timedelta indicating how far in the future the event should happen.
          event: A lambda (with no arguments) that resolves the effects of
                 the event (including enqueuing any future events).
          repeat_interval: Optional timedelta. If set, repeat the event on this
            interval after the first occurrence.
        """
        if repeat_interval:
            def repeat_event():
                event()
                self._schedule_event_relative(repeat_interval, event,
                                              repeat_interval=repeat_interval)
            self._schedule_event_at_time(self.t + delta, repeat_event)
        else:
            self._schedule_event_at_time(self.t + delta, event)