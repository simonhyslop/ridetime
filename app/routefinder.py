import json
from random import randint
from app.datafeeds import ors
from app.models import Route
from openrouteservice.directions import directions
from openrouteservice import convert


def route_to_london(start_coords):
    cutty_sark = (-0.0099676, 51.4827844)  # Destination is hardcoded as the Cutty Sark in Greenwich
    route_coords = start_coords, cutty_sark  # Coordinates tuple containing start location and Cutty Sark

    # Using ORS create a route from start location to Cutty Sark
    route = directions(client=ors, coordinates=route_coords, profile='cycling-road')

    return parse_ors(route)


# Using ORS create a route from start location to waypoint, and back again
def route_waypoint_return(start_coords, waypoint_coords):

    route_coords = start_coords, waypoint_coords, start_coords
    print("Sending coordinates to ORS: {}".format(route_coords))  # TODO: debugging

    route = directions(client=ors, coordinates=route_coords, profile='cycling-road')
    return parse_ors(route)


# Using ORS create a route between all waypoints
def route_multi_waypoint(all_coords):
    route = directions(client=ors, coordinates=all_coords, profile='cycling-road')
    return parse_ors(route)


def parse_ors(ors_output):
    distance = ors_output['routes'][0]['summary']['distance']
    duration = ors_output['routes'][0]['summary']['duration']
    geometry = ors_output['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)

    return distance, duration, decoded


def ors_roundroute(start_coords, km_distance):
    start_coords = [list(start_coords)]  # ORS requires 2D array, so converting coordinates into list
    metre_distance = int(km_distance) * 1000  # ORS requires distance in metres, so convert that here
    seed = randint(0, 5000)  # Seed value passed to ORS to randomise the route

    circular_params = {"round_trip": {"length": metre_distance, "seed": seed}}  # Params dict to pass with ORS API call

    # TODO: debugging
    print("Requesting {} km route starting at {} with seed value {}. Let's see what ORS cook up...".format(km_distance, start_coords, seed))

    # Use ORS to create a circular route
    route = directions(client=ors, coordinates=start_coords, profile='cycling-road', options=circular_params,
                       instructions='true', instructions_format='html', geometry='true')

    distance = route['routes'][0]['summary']['distance']
    duration = route['routes'][0]['summary']['duration']
    bbox = json.dumps(route.get('bbox'))
    geometry = route['routes'][0]['geometry']

    # Convert ORS response into a Route object
    ors_route = Route(distance=round(distance), duration=round(duration), bbox=bbox, polyline=geometry)

    return ors_route


def polyline_to_coords(encoded_polyline):
    decoded = convert.decode_polyline(encoded_polyline)
    return decoded['coordinates']
