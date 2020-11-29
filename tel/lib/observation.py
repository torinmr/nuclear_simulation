from abc import ABC, abstractmethod
from collections import namedtuple

def observation_stats(obs):
    """Print stats on a collection of observations."""
    return "{} TELs observed, {} non-TEL observations".format(
        sum([o.multiplicity for o in obs if o.tuid]),
        sum([o.multiplicity for o in obs if not o.tuid]))

def analysis_stats(obs):
    """Print stats on a collection of observations after analysis"""
    tp = sum([o.multiplicity for o in obs if o.tuid])
    otp = sum([o.original_multiplicity for o in obs if o.tuid])
    tpr = tp/otp if otp else 0
    fp = sum([o.multiplicity for o in obs if not o.tuid])
    ofp = sum([o.original_multiplicity for o in obs if not o.tuid])
    fpr = fp/ofp if ofp else 0
    return "{}/{} ({:.2%}) TELs observed, {}/{} ({:.2%}) non-TEL observations".format(
        tp, otp, tpr, fp, ofp, fpr)

class Observation:
    def __init__(self, t, tuid, multiplicity=1, method=None):
        """Create an observation object.
        
        Args:
          t: Timestamp of when the observation occurred.
          tuid: If set, the uid of the TEL this observation corresponds to.
            If None, then this observation does not correspond to a TEL.
          multiplicity: How many individual observations this Observation object
            corresponds to. Should be used for negative observations - for
            example, 10,000 satellite images not containing a TEL could be
            represented by a single Observation object with multiplicity 10,000,
            rather than by 10,000 individual objects.
          method: enums.DetectionMethod enum.
        """
        self.t = t
        self.tuid = tuid
        self.multiplicity = multiplicity
        self.original_multiplicity = self.multiplicity
        assert method is not None
        self.method = method

class Observer(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def observe(self, s):
        """Observe the current state of the simulation, and emit observations.
        
        Args:
          s: The simulation object.
        Returns:
          A collection of Observations representing unprocessed sensor data. Should
          include both positive observations (corresponding to any and all TELs this
          Observer can observe at the moment), and negative observations (corresponding
          to satellite images containing no TELs, for example).
        """  
        pass

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