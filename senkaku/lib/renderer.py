import folium
import os

PADDING = 1.0 # Lat/lon padding

class Renderer:
    def __init__(self, s, save_folder):
        self.s = s
        self.save_folder = save_folder
        
    def render(self, name, render_ranges=True):
        """Return a Folium map object."""
        # First we find the lat-long bounding box.
        min_lat, max_lat = float("inf"), float("-inf")
        min_lon, max_lon = float("inf"), float("-inf")

        for entity in self.s.get_all_entities():
            lat, lon = entity.location.lat, entity.location.lon
            if lat < min_lat:
                min_lat = lat
            if lat > max_lat:
                max_lat = lat
            if lon < min_lon:
                min_lon = lon
            if lon > max_lon:
                max_lon = lon
        
        # Now we create a map.
        m = folium.Map(tiles='Mapbox Bright', prefer_canvas=True)
        m.fit_bounds([(min_lat - PADDING, min_lon - PADDING),
                      (max_lat + PADDING, max_lon + PADDING)])
        
        def point(color, entity, size=1):
            folium.CircleMarker(
                radius=size,
                location=[entity.location.lat, entity.location.lon],
                color=color,
                fill=True,
                popup=entity.name
            ).add_to(m)
        def range_indicator(color, entity, interceptor):
            if render_ranges:
                folium.Circle(
                    radius=interceptor.max_range * 1000,
                    location=[entity.location.lat, entity.location.lon],
                    color=color,
                    popup='{} range'.format(interceptor.name),
                    weight=1
                ).add_to(m)
            
        # Now plot the ports.
        # This is just a rough version. See the below links for more documentation:
        # http://python-visualization.github.io/folium/quickstart.html
        # http://python-visualization.github.io/folium/modules.html
        for aegis_ashore in self.s.aegis_ashores:
            if aegis_ashore.state == 'destroyed':
                point('black', aegis_ashore, size=2)
                continue
            point('orange', aegis_ashore, size=2)
            if hasattr(aegis_ashore, 'bmd_interceptor'):
                if aegis_ashore.bmd_interceptor.state == 'operational':
                    range_indicator('orange', aegis_ashore, aegis_ashore.bmd_interceptor)
            if hasattr(aegis_ashore, 'cmd_interceptor'): 
                if aegis_ashore.cmd_interceptor.state == 'operational':
                    range_indicator('orange', aegis_ashore, aegis_ashore.cmd_interceptor)

        for airbase in self.s.airbases:
            if airbase.state == 'destroyed':
                point('black', airbase)
                continue
            point('purple', airbase)

        for aircraft in self.s.aircraft:
            point('green', aircraft)
            if hasattr(aircraft, 'aim7_interceptors'): 
                if aircraft.aim7_interceptors.state == 'operational':
                    range_indicator('green', aircraft, aircraft.aim7_interceptors)
            if hasattr(aircraft, 'aim9_interceptors'): 
                if aircraft.aim9_interceptors.state == 'operational':
                    range_indicator('green', aircraft, aircraft.aim9_interceptors)
            if hasattr(aircraft, 'aim120_interceptors'): 
                if aircraft.aim120_interceptors.state == 'operational':
                    range_indicator('green', aircraft, aircraft.aim120_interceptors)

        for launcher in self.s.launchers:
            point('red', launcher)

        for missile in self.s.missiles:
            if missile.state != 'midflight':
                continue
            if missile.kind == 'ballistic':
                point('darkorange', missile)
            elif missile.kind == 'cruise':
                point('chartreuse', missile)   

        for port in self.s.ports:
            if port.state == 'destroyed':
                point('black', port)
                continue
            point('blue', port)

        for radar in self.s.radars:
            if radar.state == 'destroyed':
                point('black', radar)
                continue
            point('pink', radar)
            if render_ranges:
                folium.Circle(
                    radius=radar.range * 1000,
                    location=[radar.location.lat, radar.location.lon],
                    color='pink',
                    popup='{} range'.format(radar.name),
                    weight=1
                ).add_to(m)

        for sam in self.s.sams:
            if sam.state == 'destroyed':
                point('black', sam)
                continue
            point('magenta', sam)
            if hasattr(sam, 'interceptor'):
                if sam.interceptor.state == 'operational':
                    range_indicator('magenta', sam, sam.interceptor)

        for ship in self.s.ships:
            point('teal', ship)
            if hasattr(ship, 'sm3_interceptors'): 
                if ship.sm3_interceptors.state == 'operational':
                    range_indicator('teal', ship, ship.sm3_interceptors)

        
        m.save(os.path.join(self.save_folder, '{}.html'.format(name)))
        return m