import timeago, datetime
from app import app


@app.template_filter('timeago')
def timeago_format(timestamp):
    return timeago.format(timestamp, datetime.datetime.utcnow())


@app.template_filter('duration')
def duration_format(time_in_seconds):
    time_in_mins = time_in_seconds/60
    return round(time_in_mins)


@app.template_filter('distance')
def distance_format(distance_in_metres):
    distance_in_km = distance_in_metres/1000
    return round(distance_in_km, 1)


@app.template_filter('routetitle')
def routetitle_format(title):
    return title if title else "Untitled Route"


@app.template_filter('is_public')
def route_public_format(route_public):
    return 'Public' if route_public else 'Private'
