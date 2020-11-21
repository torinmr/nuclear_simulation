class Renderer:
    def __init__(self, s, save_folder):
        self.s = s
        self.save_folder = save_folder
        
    def render(self):
        print("Rendering at time: ", self.s.t)