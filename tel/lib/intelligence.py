from collections import defaultdict, namedtuple, Counter
from datetime import timedelta

from lib.enums import DetectionMethod
from lib.observer import EOObserver, SARObserver, StandoffObserver, SigIntObserver, GroundSensorObserver
from lib.analyzer import ImageryAnalyzer, PassthroughAnalyzer
from lib.tracker import PerfectTracker, RealisticTracker

class Intelligence:
    """Class representing US intelligence efforts to locate TELs."""
    def __init__(self, c):
        self.eo_observer = EOObserver(c)
        self.eo_analyzer = ImageryAnalyzer(c, "EO")
        self.sar_observer = SARObserver(c)
        self.sar_analyzer = ImageryAnalyzer(c, "SAR")
        self.standoff_observer = StandoffObserver(c)
        self.standoff_analyzer = ImageryAnalyzer(c, "Standoff")
        self.sigint_observer = SigIntObserver(c)
        self.sigint_analyzer = PassthroughAnalyzer(c)
        self.ground_observer = GroundSensorObserver(c)
        self.ground_analyzer = PassthroughAnalyzer(c)
        self.perfect_tracker = PerfectTracker(c)
        self.realistic_tracker = RealisticTracker(c)
    
    def start(self, s):
        s.schedule_event_relative(lambda: self.process(s), timedelta(),
                                  repeat_interval=timedelta(minutes=1))
        self.perfect_tracker.start(s)
        self.realistic_tracker.start(s)
    
    def process(self, s):
        all_obs = []

        raw_eo_obs = self.eo_observer.observe(s)
        analyzed_eo_obs = self.eo_analyzer.analyze(raw_eo_obs, s.t)
        all_obs += analyzed_eo_obs
        
        raw_sar_obs = self.sar_observer.observe(s)
        analyzed_sar_obs = self.sar_analyzer.analyze(raw_sar_obs, s.t)
        all_obs += analyzed_sar_obs
        
        raw_standoff_obs = self.standoff_observer.observe(s)
        analyzed_standoff_obs = self.standoff_analyzer.analyze(raw_standoff_obs, s.t)
        all_obs += analyzed_standoff_obs
        
        raw_sigint_obs = self.sigint_observer.observe(s)
        analyzed_sigint_obs = self.sigint_analyzer.analyze(raw_sigint_obs, s.t)
        all_obs += analyzed_sigint_obs
        
        raw_ground_obs = self.ground_observer.observe(s)
        analyzed_ground_obs = self.ground_analyzer.analyze(raw_ground_obs, s.t)
        all_obs += analyzed_ground_obs
        
        self.perfect_tracker.assign_observations(all_obs)
        self.realistic_tracker.assign_observations(all_obs)
        

        