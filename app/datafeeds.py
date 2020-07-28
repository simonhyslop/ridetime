import openrouteservice
from openrouteservice import geocode
from config import Config

ors_key = Config.ORS_KEY  # Read OpenRouteService key from config file
ors = openrouteservice.Client(key=ors_key)  # Create client for accessing ORS


def postcode_lookup(location):  # Enables user to enter address - eventually will be used to set route start location
    geocode_result = geocode.pelias_search(ors, text=location, country='GBR')

    if len(geocode_result['features']) > 0:
        return True, geocode_result['features'][0]['geometry']['coordinates']
    else:
        return False, (0, 0)


def reverse_lookup(coordinates):  # Takes coordinates and finds the corresponding street address

    # TODO: Refine this by only loading 'layers' which are streets, rather than venues
    rev_geocode_result = geocode.pelias_reverse(ors, point=coordinates, country='GBR', size=1)

    matched_address = rev_geocode_result['features'][0]['properties']

    print("Reverse lookup result: {}".format(rev_geocode_result))
    print("Filtered result: {}".format(matched_address))
