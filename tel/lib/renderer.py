from datetime import timedelta

from lib.time import format_time

class Renderer:
    def __init__(self, save_folder):
        self.save_folder = save_folder
        self.last_render_time = None
        
    def start(self, s):
        self.render(s)
        s.schedule_event_relative(lambda: self.render(s),
                                  s.render_interval, s.render_interval)
        
    def render(self, s):
        print()
        print("*** Rendering at time:", format_time(s.t))
        for base in s.bases:
            print(base.status())
            print(base.tel_state_summary())
        s.intelligence.print_stats(s)
        print()
        self.last_render_time = s.t
        
    def final_summary(self):
        pass
        