from collections import defaultdict, namedtuple
from datetime import timedelta

from lib.eo import EOObserver, EOAnalyzer

class Intelligence:
    """Class representing US intelligence efforts to locate TELs."""
    def __init__(self):
        self.eo_observer = EOObserver()
        self.eo_analyzer = EOAnalyzer()
    
    def start(self, s):
        s.schedule_event_relative(lambda: self.process(s), timedelta(),
                                  repeat_interval=timedelta(minutes=1))
    
    def process(self, s):
        all_observations = []

        raw_eo_observations = self.eo_observer.observe(s)
        analyzed_eo_observations = self.eo_analyzer.analyze(raw_eo_observations, s.t)
        all_observations += analyzed_eo_observations
        
        # Similar stanzas for other types of observations.

        num_false_positives = 0
        obs_from_tuid = defaultdict(list)
        for obs in all_observations:
            if obs.tuid:
                obs_from_tuid[obs.tuid].append(obs)
            else:
                num_false_positives += obs.multiplicity
        
        num_tels_detected = 0
        total_num_tels = 0
        for tel in s.tels():
            total_num_tels += 1
            if tel.uid in obs_from_tuid:
                num_tels_detected += 1
        if all_observations:
            print("{} out of {} TELs detected.".format(num_tels_detected, total_num_tels))