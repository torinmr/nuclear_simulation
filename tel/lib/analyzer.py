from abc import ABC, abstractmethod
from datetime import timedelta
from numpy import random

from lib.intelligence_types import Observation, observation_stats, analysis_stats
from lib.time import format_time

class Analyzer(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def analyze(self, observations, t):
        """Analyze observations emitted by an Observer.
        
        Args:
          observations: A sequence of observations (positive and negative).
          t: Current simulation time.
        Returns:
          A collection of Observations representing what the analysis process believes
          to be TELs. Can still contain negative examples to represent false positives
          in the analysis process.
        
          The returned observations do not have to be a subset of the input observations
          - for example, they could be observations that arrived some time ago, if the
          analysis process is not instantaneous.
        """  
        pass

class ImageryAnalyzer(Analyzer):
    def __init__(self, name, ml_processing_time=timedelta(minutes=5),
                 ml_fp=.00145, ml_fn=.05, human_fp=.0005, human_fn=.05,
                 human_examples_per_minute=7800):
        self.name = name
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
        return observations
        
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
                print("{} human processing at {} done: {}".format(
                    self.name, format_time(t), analysis_stats(ret)))
                self.human_processing = None
        
        if self.ml_processing:
            start_time, obs = self.ml_processing
            # This could alternatively be done by assuming a
            # "ml_example_per_minute" value.
            if t - start_time >= self.ml_processing_time:
                self.waiting_for_human_processing = self.ml_process(obs)
                print("{} ML processing at {} done: {}".format(
                    self.name, format_time(t), analysis_stats(self.waiting_for_human_processing)))
                self.ml_processing = None

        if self.waiting_for_human_processing and not self.human_processing:
            self.human_processing = (t, self.waiting_for_human_processing)
            self.waiting_for_human_processing = None
        
        if not self.ml_processing and observations:
            self.ml_processing = (t, observations)
            print("{} data available at {}: {}".format(
                self.name, format_time(t), observation_stats(observations)))
            
        return ret