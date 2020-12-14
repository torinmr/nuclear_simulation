from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from math import floor, ceil
from typing import Dict
from uuid import uuid4

def missile_retaliation_prob(c, m):
    """Probability US missile defense successfully destroys m missiles."""
    nint = c.num_interceptors
    p = c.interceptor_kill_prob
    if m == 0:
        return 0
    return 1 - ((1-(1-p)**floor(nint/m))**(m-nint%m)) * ((1-(1-p)**ceil(nint/m))**(nint%m))

@dataclass
class AssessmentStats:
    avg_roam_time_min: float
    area_to_destroy_by_time: Dict[float, float]
    missiles_remaining: int
    retaliation_prob: float

def assess(c, t, files):
    tels_to_destroy = []
    total_roam_time = timedelta()
    for f in files.values():
        f.obs.sort()
        obs = f.obs[-1]
        total_roam_time += f.tel.roaming_time_since_observation(obs, t)
        area = f.tel.destruction_area(obs, t, t)
        # Insert a random integer (uuid) to give a total order.
        tels_to_destroy.append((area, uuid4(), f.tel, obs))
    avg_roam_time = (total_roam_time/len(tels_to_destroy)) / timedelta(minutes=1)
    
    tels_to_destroy.sort()
    arsenal = deepcopy(c.arsenal)
    remaining_tels = []
    area_to_destroy_by_time = {}
    for nuke in arsenal:
        flight_time_min = nuke.flight_time / timedelta(minutes=1)
        area_to_destroy_by_time[flight_time_min] = 0
    for area, _, tel, obs in tels_to_destroy:
        for key in area_to_destroy_by_time.keys():
            flight_time = timedelta(minutes=key)
            area_to_destroy_by_time[key] += tel.destruction_area(obs, t, t + flight_time)
        destroyed_km = 0
        num_missiles = 0
        km_to_destroy = 0
        destroyed = False
        for nuke in arsenal:
            km_to_destroy = tel.destruction_area(obs, t, t + nuke.flight_time)
            while nuke.number >= c.nukes_per_tel and destroyed_km < km_to_destroy:
                nuke.number -= c.nukes_per_tel
                destroyed_km += nuke.km2
                num_missiles += 1
            if destroyed_km >= km_to_destroy:
                destroyed = True
                break           
        if not destroyed:
            remaining_tels.append(tel)
        if c.debug:
            print('Used {} missiles to destroy {}, {:,.0f} km^2 destroyed, {:,.0f} km^2 required.'.format(
                num_missiles, tel.name, destroyed_km, km_to_destroy))
    
    missiles_remaining = len(remaining_tels)
    if c.debug:
        if len(remaining_tels) == 0:
            print('First strike possible!')
            for nuke, orig in zip(arsenal, c.arsenal):
                diff = orig.number - nuke.number
                if diff > 0:
                    print('  {} {}s used.'.format(orig.number - nuke.number, nuke.name))

        if len(remaining_tels) > 0:
            print('First strike not possible, {} TELs remaining.'.format(missiles_remaining))
            
    retaliation_prob = missile_retaliation_prob(c, missiles_remaining)
    return AssessmentStats(avg_roam_time, area_to_destroy_by_time, missiles_remaining, retaliation_prob)