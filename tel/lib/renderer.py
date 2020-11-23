class Renderer:
    def __init__(self, s, save_folder):
        self.s = s
        self.save_folder = save_folder
        self.last_render_time = None
        
    def render(self):
        print("*** Rendering at time: ", self.s.t)
        for base in self.s.bases:
            print(base.status())
            print(base.tel_state_summary())
        print()
        self.last_render_time = self.s.t