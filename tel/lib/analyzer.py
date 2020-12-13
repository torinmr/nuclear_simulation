from abc import ABC, abstractmethod
from datetime import timedelta

from lib.enums import TLOKind
from lib.intelligence_types import Observation
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
    
def timing_stats(start_t, ml_t, final_t):
    return "ML analysis started at {}, finished at {}. Human analysis finished at {}.".format(
        format_time(start_t), format_time(ml_t), format_time(final_t))

def analysis_stats(start_obs, ml_obs, final_obs):
    tp = sum([o.multiplicity for o in final_obs if o.tlo and o.tlo.kind == TLOKind.TEL])
    otp = sum([o.multiplicity for o in start_obs if o.tlo and o.tlo.kind == TLOKind.TEL])
    tpr = tp/otp if otp else 0
    fp = sum([o.multiplicity for o in final_obs if o.tlo is None or o.tlo.kind != TLOKind.TEL])
    ofp = sum([o.multiplicity for o in start_obs if o.tlo is None or o.tlo.kind != TLOKind.TEL])
    fpr = fp/ofp if ofp else 0
    return "  {}/{} ({:.2%}) TELs observed, {}/{} ({:.2%}) non-TEL observations".format(
        tp, otp, tpr, fp, ofp, fpr)
    
class ImageryAnalyzer(Analyzer):
    def __init__(self, name, ml_processing_duration=timedelta(minutes=5),
                 ml_fp=.00145, ml_fn=.05, human_fp=.0005, human_fn=.05,
                 human_examples_per_minute=7800):
        self.name = name
        self.ml_processing_duration = timedelta(minutes=5)
        self.ml_fp = ml_fp
        self.ml_fn = ml_fn
        self.human_fp = human_fp
        self.human_fn = human_fn
        self.human_examples_per_minute = human_examples_per_minute
        # (start_t, start_obs), representing data not yet processed.
        self.ml_processing = None
        # (start_t, start_obs, ml_t, ml_obs), observations finished processing by ML, not yet started by humans.
        self.waiting_for_human_processing = None
        # (start_t, start_obs, ml_t, ml_obs), representing data being processed by humans
        self.human_processing = None
        # Time when latest batch of human processing started. Only set if self.human_processing is not None.
        self.human_processing_start_t = None
        super().__init__()
        
    def process(self, observations, fp=0, fn=0):
        sampled_observations = []
        for obs in observations:
            # TODO: Update probabilities based on kind of TLO.
            if obs.tlo and obs.tlo.kind == TLOKind.TEL:
                p = 1 - fn
            else:
                p = fp
            sampled_obs = obs.sample(p)
            if sampled_obs is not None:
                sampled_observations.append(sampled_obs)
        return sampled_observations
        
    def human_process(self, observations):
        return self.process(observations, fp=self.human_fp, fn=self.human_fn)
    
    def ml_process(self, observations):
        return self.process(observations, fp=self.ml_fp, fn=self.ml_fn)
    
    def analyze(self, observations, t):
        ret = []
        
        if self.human_processing:
            start_t, start_obs, ml_t, ml_obs = self.human_processing
            num_observations = sum([o.multiplicity for o in ml_obs])
            elapsed_minutes = (t - self.human_processing_start_t).seconds / 60
            if elapsed_minutes * self.human_examples_per_minute >= num_observations:
                final_obs = self.human_process(ml_obs)
                print(timing_stats(start_t, ml_t, t))
                print(analysis_stats(start_obs, ml_obs, final_obs))
                self.human_processing = None
                self.human_processing_start_t = None
        
        if self.ml_processing:
            start_t, start_obs = self.ml_processing
            # This could alternatively be done by assuming a
            # "ml_example_per_minute" value.
            if t - start_t >= self.ml_processing_duration:
                ml_obs = self.ml_process(start_obs)
                self.waiting_for_human_processing = (start_t, start_obs, t, ml_obs)
                self.ml_processing = None

        if self.waiting_for_human_processing and not self.human_processing:
            self.human_processing = self.waiting_for_human_processing
            self.human_processing_start_t = t
            self.waiting_for_human_processing = None
        
        if not self.ml_processing and observations:
            self.ml_processing = (t, observations)
            
        return ret