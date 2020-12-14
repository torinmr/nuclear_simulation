from abc import ABC, abstractmethod
from datetime import timedelta

from lib.enums import TLOKind
from lib.intelligence_types import Observation
from lib.time import format_time

class Analyzer(ABC):
    def __init__(self, c):
        self.c = c
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
    
def timing_stats(name, start_t, ml_t, final_t):
    return "{} ML analysis started at {}, finished at {}. Human analysis finished at {}.".format(
        name, format_time(start_t), format_time(ml_t), format_time(final_t))

def analysis_stats(start_obs, ml_obs, final_obs):
    lines = ["  Positive rates per TELKind:"]
    for kind in TLOKind: 
        p = sum([o.multiplicity for o in final_obs if o.tlo_kind == kind])
        op = sum([o.multiplicity for o in start_obs if o.tlo_kind == kind])
        pr = p/op if op else 0
        lines.append("    {}: {}/{} ({:.2%})".format(kind.name, p, op, pr))
    return "\n".join(lines)
    
class ImageryAnalyzer(Analyzer):
    def __init__(self, c, name):
        super().__init__(c)
        self.name = name
        
        # (start_t, start_obs), representing data not yet processed.
        self.ml_processing = None
        # (start_t, start_obs, ml_t, ml_obs), observations finished processing by ML, not yet started by humans.
        self.waiting_for_human_processing = None
        # (start_t, start_obs, ml_t, ml_obs), representing data being processed by humans
        self.human_processing = None
        # Time when latest batch of human processing started. Only set if self.human_processing is not None.
        self.human_processing_start_t = None
        
    def process(self, observations, p_from_kind, non_tlo_positive_rate):
        sampled_observations = []
        for obs in observations:
            if obs.tlo_kind is None:
                p = non_tlo_positive_rate
            else:
                p = p_from_kind[obs.tlo_kind]

            sampled_obs = obs.sample(p)
            if sampled_obs is not None:
                sampled_observations.append(sampled_obs)
        return sampled_observations
        
    def human_process(self, observations):
        return self.process(observations, self.c.human_positive_rates, 0)
    
    def ml_process(self, observations):
        return self.process(observations, self.c.ml_positive_rates,
                            self.c.ml_non_tlo_positive_rate)
    
    def analyze(self, observations, t):
        final_obs = []
        
        if self.human_processing:
            start_t, start_obs, ml_t, ml_obs = self.human_processing
            num_observations = sum([o.multiplicity for o in ml_obs])
            elapsed_minutes = (t - self.human_processing_start_t).seconds / 60
            if elapsed_minutes * self.c.human_examples_per_minute >= num_observations:
                final_obs = self.human_process(ml_obs)
                print(timing_stats(self.name, start_t, ml_t, t))
                print(analysis_stats(start_obs, ml_obs, final_obs))
                self.human_processing = None
                self.human_processing_start_t = None
        
        if self.ml_processing:
            start_t, start_obs = self.ml_processing
            # This could alternatively be done by assuming a
            # "ml_example_per_minute" value.
            if t - start_t >= self.c.ml_processing_duration:
                ml_obs = self.ml_process(start_obs)
                self.waiting_for_human_processing = (start_t, start_obs, t, ml_obs)
                self.ml_processing = None

        if self.waiting_for_human_processing and not self.human_processing:
            self.human_processing = self.waiting_for_human_processing
            self.human_processing_start_t = t
            self.waiting_for_human_processing = None
        
        if not self.ml_processing and observations:
            self.ml_processing = (t, observations)
            
        return final_obs
    
class SigIntAnalyzer(Analyzer):
    def __init__(self, c):
        super().__init__(c)
        
    def analyze(self, observations, t):
        return observations