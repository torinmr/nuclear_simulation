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

    def _bearing_towards(self, other):
        """Return the angular bearing in radians towards the other location"""
        phi_1 = math.radians(self.lat)
        phi_2 = math.radians(other.lat)
        delta_lambda = math.radians(other.lon - self.lon)
        
        y = math.sin(delta_lambda) * math.cos(phi_2)
        x = (math.cos(phi_1) * math.sin(phi_2) -
             math.sin(phi_1) * math.cos(phi_2) * math.cos(delta_lambda))
        return math.atan2(y, x)
    
    def move_towards(self, other, distance):
        """Return a new location which is distance km towards the other location.
        
        Again uses the formula from
        https://www.movable-type.co.uk/scripts/latlong.html.
        
        Args:
          other: The other location.
          distance: Number of km to step towards the other location.
        Returns:
          A new location, distance km closer to the other location.
        """
        bearing = self._bearing_towards(other)
        
        phi_1 = math.radians(self.lat)
        lambda_1 = math.radians(self.lon)
        angular_distance = distance / EARTH_RADIUS
        
        phi_new = math.asin(
            math.sin(phi_1) * math.cos(angular_distance) +
            math.cos(phi_1) * math.sin(angular_distance) * math.cos(bearing))
        lambda_new = lambda_1 + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(phi_1),
            math.cos(angular_distance) - math.sin(phi_1) * math.sin(phi_new))  
        
        new_lat = (math.degrees(phi_new) + 540) % 360 - 180
        new_lon = (math.degrees(lambda_new) + 540) % 360 - 180
        return Location(new_lat, new_lon)
    
    def to_string(self):
        return '({}, {})'.format(self.lat, self.lon)
    
tokyo = Location(35.5895, 139.6917)
rio = Location(-22.9068, -43.1729)
assert math.fabs(tokyo.distance_to(rio) - 18580.0) < 10
assert math.fabs(rio.distance_to(tokyo) - 18580.0) < 10

