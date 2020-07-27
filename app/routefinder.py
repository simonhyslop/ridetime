from app.datafeeds import ors
from openrouteservice.directions import directions
from openrouteservice import convert


def route_to_london(start_location):
    cutty_sark = (-0.0099676, 51.4827844)  # Destination is hardcoded as the Cutty Sark in Greenwich
    route_coords = start_location, cutty_sark  # Coordinates tuple containing start location and Cutty Sark

    # Using ORS create a route from start location to Cutty Sark
    route = directions(ors, route_coords, profile='cycling-road')

    distance = route['routes'][0]['summary']['distance']
    duration = route['routes'][0]['summary']['duration']
    geometry = route['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)

    return distance, duration, decoded


# From the start coordinates, find a random point distance/2 from there, and call the ORS API to generate a route there
# and back. Then return geoJSON or whatever to be displayed on the map.
# TODO: Consider how the route will be downloadable, i.e. creating GPX file
def primitive_roundroute(start_coordinates, km_distance):
    print("Creating route for approx. {} km.".format(km_distance))
