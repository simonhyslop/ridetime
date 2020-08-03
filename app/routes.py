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
def home():
    form = LocationSearch()
    if form.validate_on_submit():  # When user submits their location, look it up using ORS API
        result_found, coords, address = datafeeds.postcode_lookup(form.location.data)
        if result_found:  # If a matching location is found, move to next page
            session['location_search'] = form.location.data
            session['start_coords'] = coords
            # flash("Location found: {}".format(address), 'info')
            return redirect('/location')
        else:  # If no location found, show an error
            flash("Location '{}' not found! Please try a different search.".format(form.location.data), 'danger')

    return render_template('index.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/location', methods=['GET', 'POST'])
def set_prefs():
    form = LocationSearch()
    # form.location.data = session.get('location_search', '')

    if form.validate_on_submit():  # When user submits their location, look it up using ORS API
        result_found, coords, address = datafeeds.postcode_lookup(form.location.data)
        if result_found:  # If a matching location is found, update page to new location
            session['location_search'] = form.location.data
            session['start_coords'] = coords
        else:  # If no location found, show an error
            flash("Location '{}' not found! Please try a different search.".format(form.location.data), 'danger')

    start_coords = session.get('start_coords')

    if not start_coords:  # Backup route in case no start coordinates are found
        flash('Location not recognised! Default location has been set instead.', 'danger')
        start_coords = -1.930556, 52.450556  # If no location provided, default to UoB

    # datafeeds.reverse_lookup(start_coords)

    return render_template('location.html', title='New route', form=form, mapbox_key=mapbox_key, start=start_coords)


@app.route('/route')
def generate_route():
    # TODO: make this more defensive so that it can handle bad inputs

    start_coords = session.get('start_coords')

    # In case we reach this page without coordinates set, use default location of Uni Birmingham campus
    if not start_coords:
        flash('Location not recognised! Default location has been set instead.', 'danger')
        start_coords = [-1.930556, 52.450556]  # Coordinates for Uni Birmingham campus

    distance_requested = request.args.get('dist', '20')  # User requested distance (in km) for how far they want to cycle. Value defaults to 20 in case nothing is set.

    bbox, distance, duration, decoded = routefinder.ors_roundroute(start_coords, distance_requested)
    distance = round(distance/1000, 1)  # Convert distance to nearest 0.1 km
    duration = round(duration/60)  # Convert time to nearest minute
    route_coords = decoded['coordinates']

    # poi_search = datafeeds.pubfinder(decoded)

    num_pubs_found = 0  # was: len(poi_search.get('features'))

    instructions = "Instructions coming soon!"

    return render_template('route.html', title='View route', mapbox_key=mapbox_key, bbox=bbox, start=start_coords,
                           route=route_coords, distance=distance, duration=duration, num_pubs_found=num_pubs_found,
                           instructions=instructions)


# Just used for testing, can likely delete
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data), 'info')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)
