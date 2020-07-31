# http://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/getting-started-with-flask.html
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
# https://getbootstrap.com/docs/4.5/getting-started/introduction/
# https://docs.mapbox.com/mapbox-gl-js/api/

from flask import render_template, flash, redirect, url_for, request, session
from app import app, datafeeds, routefinder
from app.forms import LoginForm, LocationSearch
from config import Config

mapbox_key = Config.MAPBOX_KEY  # Read Mapbox key from config file


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LocationSearch()
    if form.validate_on_submit():  # When user submits their location, look it up using ORS API
        result_found, coords, address = datafeeds.postcode_lookup(form.location.data)
        if result_found:  # If a matching location is found, move to next page
            session['start_coords'] = coords
            flash("Location found: {}".format(address), 'info')
            return redirect('/location')
        else:  # If no location found, show an error
            flash("Location '{}' not found! Please try a different search.".format(form.location.data), 'danger')

        # return redirect('/location?long={}&lat={}'.format(coords[0], coords[1]))

    return render_template('index.html', form=form)


@app.route('/location')
def set_prefs():
    start_coords = session.get('start_coords')

    if not start_coords:  # Backup route in case no start coordinates are found
        flash('Location not recognised! Default location has been set instead.', 'danger')
        start_coords = -1.930556, 52.450556  # If no location provided, default to UoB

    # datafeeds.reverse_lookup(start_coords)

    return render_template('location.html', title='New route', mapbox_key=mapbox_key, start=start_coords)


@app.route('/route')
def generate_route():
    # TODO: make this more defensive so that it can handle bad inputs

    start_coords = tuple(session.get('start_coords'))

    if not start_coords:  # Backup route in case no start coordinates are found
        flash('Location not recognised! Default location has been set instead.', 'danger')
        start_coords = -1.930556, 52.450556  # If no location provided, default to UoB

    dist = request.args.get('dist')

    distance, duration, decoded = routefinder.primitive_roundroute(start_coords, dist)
    distance = round(distance/1000, 1)  # Convert distance to nearest 0.1 km
    duration = round(duration/60)  # Convert time to nearest minute
    route_coords = decoded['coordinates']

    poi_search = datafeeds.pubfinder(decoded)

    num_pubs_found = len(poi_search.get('features'))

    return render_template('route.html', title='View route', mapbox_key=mapbox_key, start=start_coords,
                           route=route_coords, distance=distance, duration=duration, num_pubs_found=num_pubs_found)


# Just used for testing, can likely delete
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data), 'info')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)
