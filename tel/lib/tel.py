from enum import Enum

class TEL:
    """A single Transporter-Erector-Launcher.
    
    TELs are not modeled as having a precise geographic location. Instead, they are
    associated with a TEL base (which does have a location), and at any given
    moment are in one out of a set of possible states (in base, roaming, hiding in a
    tunnel, etc).
    """
    class State(Enum):
        IN_BASE = auto()
        ROAMING = auto()
    
    class Type(Enum):
        # TODO: Learn actual types of TELs.
        BASIC_TEL = auto()
    
    def __init__(self, base, type=Type.BASIC_TEL, initial_state=State.IN_BASE):
        """Initialize a TEL object.
        
        Args:
          base: The TELBase this TEL belongs to.
          type: A TEL.Type enum value.
          initial_state: A TEL.State enum value.
        """
        self.base = base
        self.type = type
        self.initial_state = initial_state
    
    