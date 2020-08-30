# Templates for powering Jinja templates, allowing us to pass variables into
# our HTML code and neatly convert them into a pretty format for display there.
# This reduces the need to manipulate data in our Python code before a page is loaded.

import timeago, datetime
from app import app


# Converts a timestamp into a more user-friendly format, e.g. '5 minutes ago'
@app.template_filter('timeago')
def timeago_format(timestamp):
    return timeago.format(timestamp, datetime.datetime.utcnow())


# Converts time in seconds to minutes, rounded to the nearest minute
@app.template_filter('duration')
def duration_format(time_in_seconds):
    time_in_mins = time_in_seconds/60
    return round(time_in_mins)


# Converts metre distance to kilometres, rounding to nearest 0.1km
@app.template_filter('distance')
def distance_format(distance_in_metres):
    distance_in_km = distance_in_metres/1000
    return round(distance_in_km, 1)


# Displays the route title if present, else 'Untitled Route'
@app.template_filter('routetitle')
def routetitle_format(title):
    return title if title else "Untitled Route"


# Converts boolean of 'is_public' to a more user-friendly 'Public' or 'Private'
@app.template_filter('is_public')
def route_public_format(route_public):
    return 'Public' if route_public else 'Private'
