from abc import ABC, abstractmethod
from collections import namedtuple

class Observation:
    def __init__(self, t, tuid, multiplicity):
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
        """
        self.tuid = tuid
        self.multiplicity = multiplicity

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
    def analyze(self, observations):
        """Analyze observations emitted by an Observer.
        
        Args:
          observations: A sequence of observations (positive and negative).
        Returns:
          A collection of Observations representing what the analysis process believes
          to be TELs. Can still contain negative examples to represent false positives
          in the analysis process.
        
          The returned observations do not have to be a subset of the input observations
          - for example, they could be observations that arrived some time ago, if the
          analysis process is not instantaneous.
        """  
        pass