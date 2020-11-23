class Renderer:
    def __init__(self, s, save_folder):
        self.s = s
        self.save_folder = save_folder
        self.last_render_time = None
        
    def render(self):
        print("Rendering at time: ", self.s.t)
        print(self.s.base.status())
        print(self.s.base.tel_state_summary())
        print()
        self.last_render_time = self.s.t