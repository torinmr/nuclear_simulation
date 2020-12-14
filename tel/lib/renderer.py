from collections import defaultdict
import csv
from datetime import timedelta
import os

import matplotlib
from matplotlib.dates import DateFormatter, ConciseDateFormatter, HourLocator, AutoDateLocator
import matplotlib.pyplot as plt
import numpy as np

from lib.time import format_time

def time_plotter(ax, ts, y, param_dict):
    x = matplotlib.dates.date2num(ts)
    tz = ts[0].tzinfo
    ax.set_xlabel('Simulation time')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M', tz=tz))
    ax.xaxis.set_major_locator(AutoDateLocator(tz=tz))
    out = ax.plot(x, y, linewidth=.5, **param_dict)

class Renderer:
    def __init__(self, c, save_folder):
        self.c = c
        self.save_folder = save_folder  
        
    def start(self, s):
        self.render(s)
        s.schedule_event_relative(lambda: self.render(s),
                                  s.render_interval, s.render_interval)
        
    def render(self, s):
        if self.c.debug:
            print("*** Rendering at time:", format_time(s.t))
            if s.bases:
                for base in s.bases:
                    print(base.status())
                    print(base.tel_state_summary())

                s.intelligence.perfect_tracker.analyze_files(s.t)
            print()
        
    def final_summary(self, s):
        ts = s.intelligence.ts
        avg_roam_time_min = []
        area_to_destroy_by_time = defaultdict(list)
        missiles_remaining = []
        mated_missiles_remaining = []
        retaliation_prob = []
        
        if not os.path.exists(self.c.output_dir):
            os.makedirs(self.c.output_dir)
        csv_path = self.c.output_dir + '/raw.csv'
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['time', 'avg_roam_time_min']
            fieldnames += ['area_to_destroy_{}min'.format(time)
                           for time in s.intelligence.assessment_stats[0].area_to_destroy_by_time]
            fieldnames += ['missiles_remaining', 'mated_missiles_remaining', 'retaliation_prob']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t, stats in zip(ts, s.intelligence.assessment_stats):
                avg_roam_time_min.append(stats.avg_roam_time_min)
                for time, area in stats.area_to_destroy_by_time.items():
                    area_to_destroy_by_time[time].append(area / 1000)
                missiles_remaining.append(stats.missiles_remaining)
                mated_missiles_remaining.append(stats.mated_missiles_remaining)
                retaliation_prob.append(stats.retaliation_prob)
                d = {
                    'time': format_time(t),
                    'avg_roam_time_min': '{:.1f}'.format(stats.avg_roam_time_min),
                    'missiles_remaining': stats.missiles_remaining,
                    'mated_missiles_remaining': stats.mated_missiles_remaining,
                    'retaliation_prob': '{:.4f}'.format(stats.retaliation_prob),
                }
                for time, area in stats.area_to_destroy_by_time.items():
                    d['area_to_destroy_{}min'.format(time)] = '{:,.0f}'.format(area)
                writer.writerow(d)    
        
        plt.style.use('seaborn-whitegrid')

        fig, ax = plt.subplots()
        fig.dpi = 200
        for time, areas in area_to_destroy_by_time.items():
            time_plotter(ax, ts, areas,
                         {'label': '{}m delay'.format(time)})
        ax.set_ylabel('Area to destroy (1000 km^2)')
        ax.legend(loc='upper left')
        plt.savefig(self.c.output_dir + '/area.png')

        fig, ax = plt.subplots()
        fig.dpi = 200
        time_plotter(ax, ts, avg_roam_time_min, {})
        ax.set_ylabel('Average roaming time since last detection')
        plt.savefig(self.c.output_dir + '/roam.png')
        
        fig, ax = plt.subplots()
        fig.dpi = 200
        time_plotter(ax, ts, missiles_remaining, {'label': 'Total TELs remaining'})
        time_plotter(ax, ts, mated_missiles_remaining, {'label': 'Mated TELs remaining'})
        ax.set_ylabel('Number remaining')
        ax.legend(loc='upper left')
        plt.savefig(self.c.output_dir + '/remaining.png')
        
        fig, ax = plt.subplots()
        fig.dpi = 200
        time_plotter(ax, ts, retaliation_prob, {'label': 'Retaliation probability'})
        ax.set_ylabel('Probability of successful retaliation')
        plt.savefig(self.c.output_dir + '/retaliation.png')

        