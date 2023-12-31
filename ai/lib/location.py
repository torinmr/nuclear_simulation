import math

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
    
    def to_string(self):
        return '({}, {})'.format(self.lat, self.lon)
    
tokyo = Location(35.5895, 139.6917)
rio = Location(-22.9068, -43.1729)
assert math.fabs(tokyo.distance_to(rio) - 18580.0) < 10
assert math.fabs(rio.distance_to(tokyo) - 18580.0) < 10