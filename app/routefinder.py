from random import randint
from app.datafeeds import ors
from openrouteservice.directions import directions
from openrouteservice import convert


def route_to_london(start_coords):
    cutty_sark = (-0.0099676, 51.4827844)  # Destination is hardcoded as the Cutty Sark in Greenwich
    route_coords = start_coords, cutty_sark  # Coordinates tuple containing start location and Cutty Sark

    # Using ORS create a route from start location to Cutty Sark
    route = directions(client=ors, coordinates=route_coords, profile='cycling-road')

    return parse_ors(route)


def route_waypoint_return(start_coords, waypoint_coords):

    route_coords = start_coords, waypoint_coords, start_coords
    print("Sending coordinates to ORS: {}".format(route_coords))

    # Using ORS create a route from start location to waypoint, and back again
    route = directions(client=ors, coordinates=route_coords, profile='cycling-road')

    return parse_ors(route)


def route_multi_waypoint(all_coords):

    # Using ORS create a route between all waypoints
    route = directions(client=ors, coordinates=all_coords, profile='cycling-road')

    return parse_ors(route)


def parse_ors(ors_output):
    distance = ors_output['routes'][0]['summary']['distance']
    duration = ors_output['routes'][0]['summary']['duration']
    geometry = ors_output['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)

    return distance, duration, decoded


# From the start coordinates, find a random point distance/2 from there, and call the ORS API to generate a route there
# and back. Then return geoJSON or whatever to be displayed on the map.
# TODO: Consider how the route will be downloadable, i.e. creating GPX file
def primitive_roundroute(start_coords, km_distance):
    print("Creating route for approx. {} km.".format(km_distance))

    waypoint1_coords = start_coords[0] + 0.01, start_coords[1] - 0.005  # Was +0.1, -0.05
    waypoint2_coords = start_coords[0], start_coords[1] - 0.01  # Was 0,-0.1

    # Create a list of coordinates from start, visiting waypoints, then looping back to start
    multi_waypoint_coords = start_coords, waypoint1_coords, waypoint2_coords, start_coords

    return route_multi_waypoint(multi_waypoint_coords)


def ors_roundroute(start_coords, km_distance):
    start_coords = [list(start_coords)]  # ORS requires 2D array, so converting coordinates into list
    metre_distance = int(km_distance) * 1000  # ORS requires distance in metres, so convert that here
    seed = randint(0, 5000)  # Seed value passed to ORS to randomise the route

    # Params dict to pass as part of ORS API call
    circular_params = {"round_trip": {"length": metre_distance, "seed": seed}}

    print("Requesting {} km route starting at {} with seed value {}. Let's see what ORS cook up...".format(km_distance, start_coords, seed))

    # Use ORS to create a circular route
    route = directions(client=ors, coordinates=start_coords, profile='cycling-road', options=circular_params,
                       instructions='true', instructions_format='html', geometry='true')

    bbox = route.get('bbox')
    distance = route['routes'][0]['summary']['distance']
    duration = route['routes'][0]['summary']['duration']
    geometry = route['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)

    return bbox, distance, duration, decoded
