# Here we handle route creation, including calling the Openrouteservice (ORS) API, so
# queries have to be correctly formatted, and responses need to be handled/parsed
# so that they are in a suitable format for our other code.
#
# ORS library can be found here: https://github.com/GIScience/openrouteservice-py

import json
from random import randint
from app.datafeeds import ors
from app.models import Route
from openrouteservice.directions import directions


# Takes input of the user's start location and desired route distance, and converts
# these into the format required by the ORS API. Then builds the API query and calls
# the API (using the ORS library). The API result is parsed into a more useful format
# for our purposes - which we do by creating a new Route object and returning that.
def ors_roundroute(start_coords, km_distance):
    start_coords = [list(start_coords)]  # ORS requires 2D array, so converting coordinates into list
    metre_distance = int(km_distance) * 1000  # ORS requires distance in metres, so convert that here
    seed = randint(0, 5000)  # Seed value passed to ORS to randomise the route

    circular_params = {"round_trip": {"length": metre_distance, "seed": seed}}  # Params dict to pass with ORS API call

    # Use ORS to create a circular route, and store the API response as 'route' for now
    route = directions(client=ors, coordinates=start_coords, profile='cycling-road', options=circular_params,
                       instructions='true', instructions_format='html', geometry='true')

    # Parse the API response into the components we require to store the route
    distance = route['routes'][0]['summary']['distance']
    duration = route['routes'][0]['summary']['duration']
    bbox = json.dumps(route.get('bbox'))
    geometry = route['routes'][0]['geometry']

    # Create a Route object based on the API response
    ors_route = Route(distance=round(distance), duration=round(duration), bbox=bbox, polyline=geometry)

    return ors_route
