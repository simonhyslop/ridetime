import openrouteservice
from openrouteservice import geocode
from openrouteservice.directions import directions

ors_key = open('ors_key').readline()  # Read OpenRouteService key from file
ors = openrouteservice.Client(key=ors_key)  # Create client for accessing ORS


def postcode_lookup(location):  # Enables user to enter address - eventually will be used to set route start location
    geocode_result = geocode.pelias_search(ors, text=location, country='GBR')

    return tuple((geocode_result['features'][0]['geometry']['coordinates']))


def reverse_lookup(coordinates):  # Takes coordinates and finds the corresponding street address

    # TODO: Refine this by only loading 'layers' which are streets, rather than venues
    rev_geocode_result = geocode.pelias_reverse(ors, point=coordinates, country='GBR', size=1)

    matched_address = rev_geocode_result['features'][0]['properties']

    print("Used those coordinates to look up the address:",
          matched_address.get('street'), matched_address.get('locality'))


def route_to_london(start_location):
    cutty_sark = (-0.0099676, 51.4827844)  # Destination is hardcoded as the Cutty Sark in Greenwich
    route_coords = start_location, cutty_sark  # Coordinates tuple containing start location and Cutty Sark

    route = directions(ors, route_coords,
                       profile='cycling-road')  # Using ORS create a route from start location to Cutty Sark

    return route
