from app.datafeeds import ors
from openrouteservice.directions import directions
from openrouteservice import convert


def route_to_london(start_coords):
    cutty_sark = (-0.0099676, 51.4827844)  # Destination is hardcoded as the Cutty Sark in Greenwich
    route_coords = start_coords, cutty_sark  # Coordinates tuple containing start location and Cutty Sark

    # Using ORS create a route from start location to Cutty Sark
    route = directions(ors, route_coords, profile='cycling-road')

    return parse_ors(route)


def route_waypoint_return(start_coords, waypoint_coords):

    route_coords = start_coords, waypoint_coords, start_coords
    print("Sending coordinates to ORS: {}".format(route_coords))

    # Using ORS create a route from start location to waypoint, and back again
    route = directions(ors, route_coords, profile='cycling-road')

    return parse_ors(route)


def route_multi_waypoint(all_coords):

    # Using ORS create a route between all waypoints
    route = directions(ors, all_coords, profile='cycling-road')

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
