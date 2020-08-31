# Here we coordinate our external datafeeds (i.e. Openrouteservice), handling
# authorisation using our API key, and use functions to query the API and
# return the results in a format useful for our application.
#
# ORS library can be found here: https://github.com/GIScience/openrouteservice-py

import openrouteservice  # Using Openrouteservice library to reduce the code required to query their API
from openrouteservice import convert, geocode
from config import Config

ors_key = Config.ORS_KEY  # Read OpenRouteService key from config file
ors = openrouteservice.Client(key=ors_key)  # Create client for accessing ORS


# Takes input of a route (in the format of an encoded polyline), uses the Openrouteservice
# library to decode it, then returns only the coordinates of the route, discarding the rest.
def polyline_to_coords(encoded_polyline):
    decoded = convert.decode_polyline(encoded_polyline)
    return decoded['coordinates']


# Enables user to enter address, returns coordinates which are used to set route start location
def postcode_lookup(location):
    geocode_result = geocode.pelias_search(ors, text=location, country='GBR')  # Query the API, limiting results to UK
    features = geocode_result.get('features')

    if len(features) > 0:  # If API returns a match, return the top match
        coordinates = features[0]['geometry']['coordinates']
        address = features[0]['properties']
        # Format address with name and region. If no region found, show locality instead.
        address_pretty = address.get('name')
        return True, coordinates, address_pretty
    else:  # If there are no matches, fail gracefully
        return False, (0, 0), "Not found"
