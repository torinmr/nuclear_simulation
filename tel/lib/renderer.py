from datetime import timedelta

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from lib.time import format_time

class Renderer:
    def __init__(self, save_folder):
        self.save_folder = save_folder
        self.last_render_time = None
        # self.times = []
        # self.fp_rate = []
        # self.avg_age = []
        
        
    def start(self, s):
        self.render(s)
        s.schedule_event_relative(lambda: self.render(s),
                                  s.render_interval, s.render_interval)
        self.collect_stats(s)
        s.schedule_event_relative(lambda: self.collect_stats(s),
                                  timedelta(minutes=1), timedelta(minutes=1))
        
    def collect_stats(self, s):
        pass
        #    avg_age, fp_rate = s.intelligence.stats(s)
        #    self.times.append(s.t)
        #    self.fp_rate.append(fp_rate)
        #    self.avg_age.append(avg_age.seconds / 60)
        
    def render(self, s):
        print()
        print("*** Rendering at time:", format_time(s.t))
        for base in s.bases:
            print(base.status())
            print(base.tel_state_summary())

        s.intelligence.perfect_tracker.analyze_files(s.t)
        #s.intelligence.realistic_tracker.analyze_files(s.t)
        print()
        self.last_render_time = s.t
        
    def final_summary(self):
        pass
    
        # plt.style.use('seaborn-whitegrid')
        # fig = plt.figure()
        # ax = plt.axes()
        
        # x = matplotlib.dates.date2num(self.times)
        # ax.plot(x, self.fp_rate)
        # ax.plot(x, self.avg_age)
        