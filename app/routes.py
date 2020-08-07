# http://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/getting-started-with-flask.html
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
# https://getbootstrap.com/docs/4.5/getting-started/introduction/
# https://docs.mapbox.com/mapbox-gl-js/api/

import json, timeago, datetime
from flask import render_template, flash, redirect, url_for, request, session
from app import app, db, datafeeds, routefinder
from app.forms import LoginForm, LocationSearch
from config import Config
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from app.oauth import OAuthSignIn
from app.models import User, Route

mapbox_key = Config.MAPBOX_KEY  # Read Mapbox key from config file


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LocationSearch()
    if form.validate_on_submit():  # When user submits their location, look it up using ORS API
        result_found, coords, address = datafeeds.postcode_lookup(form.location.data)
        if result_found:  # If a matching location is found, move to next page
            session['location_search'] = form.location.data
            session['start_coords'] = coords
            # flash("Location found: {}".format(address), 'info')
            return render_template('index.html', no_location=False, location_input=form, mapbox_key=mapbox_key, start=coords)
        else:  # If no location found, show an error
            flash("Location '{}' not found! Please try a different search.".format(form.location.data), 'danger')

    return render_template('index.html', no_location=True, location_input=form, mapbox_key=mapbox_key, start=None)


@app.route('/about')
def about():
    return render_template('about.html')


# TODO: make this more defensive so that it can handle bad inputs
@app.route('/route')
def generate_route():

    start_coords = session.get('start_coords')

    # In case we reach this page without coordinates set, use default location of Uni Birmingham campus
    if not start_coords:
        flash("We didn't get your location, so have set it to Birmingham for you!", 'danger')
        start_coords = [-1.930556, 52.450556]  # Coordinates for Uni Birmingham campus

    # User requested distance (in km) for how far they want to cycle. Defaults to 20 in case nothing is set.
    distance_requested = request.args.get('dist', '20')

    route = routefinder.ors_roundroute(start_coords, distance_requested)

    # Storing raw values to DB (really just testing for now)
    print("Saving route to DB: {}".format(route))
    db.session.add(route)
    db.session.commit()

    distance = round(route.distance / 1000, 1)  # Convert distance to nearest 0.1 km
    duration = round(route.duration / 60)  # Convert time to nearest minute

    route_coords = routefinder.polyline_to_coords(route.polyline)

    # poi_search = datafeeds.pubfinder(decoded)
    num_pubs_found = 0  # was: len(poi_search.get('features'))

    instructions = "Instructions coming soon!"

    return render_template('create.html', title='View Route', mapbox_key=mapbox_key, bbox=json.loads(route.bbox),
                           coords=route_coords,
                           distance=distance, duration=duration, num_pubs_found=num_pubs_found,
                           instructions=instructions)


# Just used for testing, can likely delete
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Login')


# New login method for Facebook and other OAuth
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


# After user logs in on Facebook/OAuth, this brings them back to the app
@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id = oauth.callback()
    if social_id is None:
        flash('Authentication failed.', 'danger')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete. Thanks for joining!', 'success')
    else:
        flash('Welcome back!', 'success')
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/saved')
def saved():
    all_routes = Route.query.filter().order_by(Route.timestamp.desc())

    display_routes = all_routes  # For now, let's display all routes from DB when user loads this page

    return render_template('allroutes.html', title='Saved Routes', routes=display_routes)


@app.route('/saved/<route_id>')
def saved_route(route_id):
    if current_user.is_anonymous:
        flash('To view saved routes, you will need to first sign in.', 'warning')
        return redirect(url_for('login'))

    route = Route.query.filter_by(id=route_id).first_or_404()

    if not route.title:
        route.title = "Untitled Route"

    distance = round(route.distance / 1000, 1)  # Convert distance to nearest 0.1 km
    duration = round(route.duration / 60)  # Convert time to nearest minute

    route_coords = routefinder.polyline_to_coords(route.polyline)

    return render_template('route.html', title='View Route #{}'.format(route.id), mapbox_key=mapbox_key, route=route,
                           bbox=json.loads(route.bbox), coords=route_coords, distance=distance, duration=duration)


# TODO: should probably move this to separate file
@app.template_filter('timeago')
def timeago_format(timestamp):
    return timeago.format(timestamp, datetime.datetime.utcnow())
