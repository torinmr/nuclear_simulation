class Entity:
    """Base class for all entities in the simulation.
    
    Should be used as the base class for anything which physically exists
    in the world and is not a component of a larger object. So a SAM
    object should inherit from Entity, but the InterceptorSystem object
    which is a member of the SAM object should not inherit from Entity.
    """
    def __init__(self, s, name, location):
        self.s = s
        self.name = name
        self.location = location
    
    def status_string(self):
        return '{} {}'.format(self.name, self.location.to_string())