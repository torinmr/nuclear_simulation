from numpy import random

from lib.observation import Observation, Observer

class SARObserver(Observer):
    def __init__(self):
        super().__init__()
    
    def observe(self, s):
        return []