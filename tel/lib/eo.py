from lib.observation import Observer, Analyzer

class EOObserver(Observer):
    def __init__(self):
        super().__init__()
    
    def observe(self, s):
        return []

class EOAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()
    
    def analyze(self, observations):
        return []