from collections import defaultdict, namedtuple, Counter
from datetime import timedelta

from lib.enums import DetectionMethod
from lib.eo import EOObserver
from lib.imagery_analyzer import ImageryAnalyzer
from lib.sar import SARObserver

class DetectionStatus:
    def __init__(self, t, method):
        """Current detection status of a given TEL.
        
        TELs that have never been detected should be modeled by None rather
        than a DetectionStatus object.
        
        Args:
          t: Time of latest detection.
          method: enums.DetectionStatus indicating how it was observed.
        """
        self.t = t
        self.method = method
        

class Intelligence:
    """Class representing US intelligence efforts to locate TELs."""
    def __init__(self):
        self.eo_observer = EOObserver()
        self.eo_analyzer = ImageryAnalyzer("EO")
        self.sar_observer = SARObserver()
        self.sar_analyzer = ImageryAnalyzer("SAR")
        # Map from tuid to DetectionStatus
        self.detection_map = {}
        # Map from enums.DetectionMethod to number of false positives
        # (from most recent run of that method)
        self.fp_map = Counter()
    
    def start(self, s):
        self.detection_map = {tel.uid: DetectionStatus(s.t, DetectionMethod.INITIAL)
                              for tel in s.tels()}
        s.schedule_event_relative(lambda: self.process(s), timedelta(),
                                  repeat_interval=timedelta(minutes=1))
    
    def process(self, s):
        all_observations = []

        raw_eo_observations = self.eo_observer.observe(s)
        analyzed_eo_observations = self.eo_analyzer.analyze(raw_eo_observations, s.t)
        all_observations += analyzed_eo_observations
        
        raw_sar_observations = self.sar_observer.observe(s)
        analyzed_sar_observations = self.sar_analyzer.analyze(raw_sar_observations, s.t)
        all_observations += analyzed_sar_observations

        new_fp_map = Counter()
        for obs in all_observations:
            if obs.tuid:
                if obs.tuid not in self.detection_map or self.detection_map[obs.tuid].t <= obs.t:
                    self.detection_map[obs.tuid] = DetectionStatus(obs.t, obs.method)
            else:
                new_fp_map[obs.method] += obs.multiplicity
        
        for method, count in new_fp_map.items():
            if count > 0:
                self.fp_map[method] = count
                
    # TODO: Refactor redundant cod between this and print_stats().
    def stats(self, s):
        tels_detected_per_method = Counter()
        total_age = timedelta()
        total_num_tels = 0
        for tel in s.tels():
            total_num_tels += 1
            if tel.uid in self.detection_map:
                obs = self.detection_map[tel.uid]
                tels_detected_per_method[obs.method] += 1
                total_age += s.t - obs.t

        total_tels_detected = sum(tels_detected_per_method.values())
        avg_age = total_age / total_tels_detected
        total_fp = sum(self.fp_map.values())
        return avg_age, total_fp
        
    def print_stats(self, s):
        tels_detected_per_method = Counter()
        total_age = timedelta()
        total_num_tels = 0
        for tel in s.tels():
            total_num_tels += 1
            if tel.uid in self.detection_map:
                obs = self.detection_map[tel.uid]
                tels_detected_per_method[obs.method] += 1
                total_age += s.t - obs.t

        total_tels_detected = sum(tels_detected_per_method.values())
        avg_age = total_age / total_tels_detected
        method_summary = ", ".join("{}={}".format(method.name, count)
                                   for method, count in tels_detected_per_method.items())
        print("{} out of {} TELs detected, with average age {} ({})".format(
            total_tels_detected, total_num_tels, avg_age, method_summary))
        
        total_fp = sum(self.fp_map.values())
        fp_summary = ", ".join("{}={}".format(method.name, count)
                               for method, count in self.fp_map.items())
        if total_fp > 0:
            print("{} recent false positives ({})".format(total_fp, fp_summary))