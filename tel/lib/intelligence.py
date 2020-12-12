from collections import defaultdict, namedtuple, Counter
from datetime import timedelta

from lib.enums import DetectionMethod
from lib.observer import EOObserver, SARObserver
from lib.analyzer import ImageryAnalyzer
from lib.tracker import PerfectTracker, RealisticTracker

class Intelligence:
    """Class representing US intelligence efforts to locate TELs."""
    def __init__(self):
        self.eo_observer = EOObserver()
        self.eo_analyzer = ImageryAnalyzer("EO")
        self.sar_observer = SARObserver()
        self.sar_analyzer = ImageryAnalyzer("SAR")
        self.perfect_tracker = PerfectTracker()
        self.realistic_tracker = RealisticTracker()
    
    def start(self, s):
        s.schedule_event_relative(lambda: self.process(s), timedelta(),
                                  repeat_interval=timedelta(minutes=1))
        self.perfect_tracker.start(s)
        self.realistic_tracker.start(s)
    
    def process(self, s):
        all_observations = []

        raw_eo_observations = self.eo_observer.observe(s)
        analyzed_eo_observations = self.eo_analyzer.analyze(raw_eo_observations, s.t)
        all_observations += analyzed_eo_observations
        
        raw_sar_observations = self.sar_observer.observe(s)
        analyzed_sar_observations = self.sar_analyzer.analyze(raw_sar_observations, s.t)
        all_observations += analyzed_sar_observations
        
        self.perfect_tracker.assign_observations(all_observations)
        self.realistic_tracker.assign_observations(all_observations)

        