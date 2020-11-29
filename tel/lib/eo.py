from datetime import timedelta
from numpy import random

from lib.observation import Observation, Observer, Analyzer

def stats(obs):
    return "{} TELs observed, {} non-TEL observations".format(
        sum([o.multiplicity for o in obs if o.tuid]),
        sum([o.multiplicity for o in obs if not o.tuid]))

class EOObserver(Observer):
    def __init__(self):
        super().__init__()
    
    def observe(self, s):       
        # TODO(Ben): Is there any natural delay (> 1 minute) in collecting
        #   satellite images and transmitting them to the US for analysis?
        observations = []
        for tel in s.tels():
            base = tel.base
            if base.location.is_night(s.t):
                continue
            # With 70% cloud cover, each TEL has a 30% chance of being visible.
            if random.random() < base.cloud_cover:
                continue
            observations.append(Observation(s.t, tel.uid))
        
        # TODO: How does this interact with TEL state? Do we assume that when
        #   they're in the base they're easily visible, or totally invisible
        #   (if they're in a bunker or something).
        observations.append(Observation(s.t, None, multiplicity=20_000_000))
        return observations

class EOAnalyzer(Analyzer):
    def __init__(self, ml_processing_time=timedelta(minutes=5),
                 ml_fp=.00145, ml_fn=.05, human_fp=.0005, human_fn=.05,
                 human_examples_per_minute=7800):
        self.ml_processing_time = timedelta(minutes=5)
        self.ml_fp = ml_fp
        self.ml_fn = ml_fn
        self.human_fp = human_fp
        self.human_fn = human_fn
        self.human_examples_per_minute = human_examples_per_minute
        # (start_time, observations), representing data not yet processed.
        self.ml_processing = None
        # observations finished processing by ML, not yet started by humans.
        self.waiting_for_human_processing = None
        # (start_time, observations), representing data not yet processed (by humans)
        self.human_processing = None
        super().__init__()
        
    def process(self, observations, fp=0, fn=0):
        for obs in observations:
            if obs.tuid:
                p = 1 - fn
            else:
                p = fp
            obs.multiplicity = random.binomial(n=obs.multiplicity, p=p)
        return list(filter(lambda o: o.multiplicity > 0, observations))
        
    def human_process(self, observations):
        return self.process(observations, fp=self.human_fp, fn=self.human_fn)
    
    def ml_process(self, observations):
        return self.process(observations, fp=self.ml_fp, fn=self.ml_fn)
    
    def analyze(self, observations, t):
        ret = []
        
        if self.human_processing:
            start_time, obs = self.human_processing
            num_observations = sum([o.multiplicity for o in obs])
            elapsed_minutes = (t - start_time).seconds / 60
            if elapsed_minutes * self.human_examples_per_minute >= num_observations:
                ret = self.human_process(obs)
                print("Finished human processing at time {}: {}".format(t, stats(ret)))
                self.human_processing = None
        
        if self.ml_processing:
            start_time, obs = self.ml_processing
            # This could alternatively be done by assuming a
            # "ml_example_per_minute" value.
            if t - start_time >= self.ml_processing_time:
                self.waiting_for_human_processing = self.ml_process(obs)
                print("Finished ML processing at time {}: {}".format(t, stats(self.waiting_for_human_processing)))
                self.ml_processing = None

        if self.waiting_for_human_processing and not self.human_processing:
            self.human_processing = (t, self.waiting_for_human_processing)
            self.waiting_for_human_processing = None
        
        if not self.ml_processing:
            self.ml_processing = (t, observations)
            print("EO data available at {}: {}".format(t, stats(observations)))
            
        return ret