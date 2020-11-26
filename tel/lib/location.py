from datetime import datetime
from dateutil import tz
import math
import suntime

from lib.enums import TimeOfDay

EARTH_RADIUS = 6371  # In kilometers

class Location:
    """Location objects are immutable. Instead of modifying them, make a new location object."""
    
    def __init__(self, lat, lon):
        """Construct a location.

        lat, lon: Latitude and longitude, in signed decimal degrees where
                  negative indicates west/south. E.g. Tokyo is
                  (35.6895, 139.6917), and Rio de Janeiro is
                  (-22.9068, -43.1729).
        """
        self.lat = float(lat)
        self.lon = float(lon)
        
    def distance_to(self, other):
        """Gives the distance between this location and another location.
        
        Uses the haversine formula as described here:
        https://www.movable-type.co.uk/scripts/latlong.html
           
        Args:
          other: The other location.
        Returns:
          Great circle distance in km between the locations. 
        """
        phi_1 = math.radians(self.lat)
        phi_2 = math.radians(other.lat)
        delta_phi = math.radians(other.lat - self.lat)
        delta_lambda = math.radians(other.lon - self.lon)
        
        a = (math.pow(math.sin(delta_phi/2), 2) +
             math.cos(phi_1) * math.cos(phi_2) *
             math.pow(math.sin(delta_lambda/2), 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return EARTH_RADIUS * c

    def get_time_of_day(self, t):
        """Returns a TimeOfDay enum indicating if it's daytime or nighttime.
        
        Args:
          t: Timezone-aware time (such as simulation.t).
        """
        sun = suntime.Sun(self.lat, self.lon)
        today = t.date()
        sunrise = sun.get_local_sunrise_time(date=today, local_time_zone=t.tzinfo)
        sunset = sun.get_local_sunset_time(date=today, local_time_zone=t.tzinfo)
        if sunrise.timetz() < t.timetz() < sunset.timetz():
            return TimeOfDay.DAY
        else:
            return TimeOfDay.NIGHT
        
    def is_day(self, t):
        return self.get_time_of_day(t) == TimeOfDay.DAY
    
    def is_night(self, t):
        return self.get_time_of_day(t) == TimeOfDay.NIGHT
    
    def to_string(self):
        return '({}, {})'.format(self.lat, self.lon)
    
# Tests
tokyo = Location(35.5895, 139.6917)
rio = Location(-22.9068, -43.1729)
assert math.fabs(tokyo.distance_to(rio) - 18580.0) < 10
assert math.fabs(rio.distance_to(tokyo) - 18580.0) < 10
shanghai = Location(31.23, 121.47)
shanghai_tz =  tz.gettz('Asia/Shanghai')
assert shanghai.get_time_of_day(datetime.fromisoformat('2021-01-20T10:00:00+08:00')) == TimeOfDay.DAY
assert shanghai.get_time_of_day(datetime.fromisoformat('2021-01-20T06:00:00+08:00')) == TimeOfDay.NIGHT

