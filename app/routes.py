# http://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/getting-started-with-flask.html
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
# https://getbootstrap.com/docs/4.5/getting-started/introduction/
# https://docs.mapbox.com/mapbox-gl-js/api/

import json, timeago, datetime
from flask import render_template, flash, redirect, url_for, request, session, jsonify
from app import app, db, datafeeds, routefinder
from app.forms import LocationSearch
from config import Config
from flask_login import login_user, logout_user, current_user, login_required
from app.oauth import OAuthSignIn
from app.models import User, Route

mapbox_key = Config.MAPBOX_KEY  # Read Mapbox key from config file


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def homepage(header=True):
    form = LocationSearch()
    if form.validate_on_submit():  # When user submits their location, look it up using ORS API
        result_found, coords, address = datafeeds.postcode_lookup(form.location.data)
        if result_found:  # If a matching location is found, move to next page
            session['start_location'] = address
            session['start_coords'] = coords
            # flash("Location found: {}".format(address), 'info')
            return render_template('index.html', header=False, location_input=form, mapbox_key=mapbox_key,
                                   start=coords)
        else:  # If no location found, show an error
            flash("Location '{}' not found! Please try a different search.".format(form.location.data), 'danger')

    return render_template('index.html', header=header, no_location=True, location_input=form,
                           mapbox_key=mapbox_key, start=None)


@app.route('/start', methods=['GET', 'POST'])  # Same view as homepage, but with intro header hidden (header:False)
def start_page():
    return homepage(False)


@app.route('/about')
def about():
    return render_template('about.html', header=True)


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

    address = session.get('start_location')
    if address:
        route.title = "Route near {}".format(address)

    # Storing Route to DB without user_id set
    db.session.add(route)
    db.session.commit()

    session['unsaved_route_id'] = route.id  # Store the Route ID so that we can later assign it to a user

    route_coords = routefinder.polyline_to_coords(route.polyline)

    # poi_search = datafeeds.pubfinder(decoded)
    num_pubs_found = 0  # was: len(poi_search.get('features'))

    instructions = "Instructions coming soon!"

    return render_template('create.html', header=False, title='View Route', mapbox_key=mapbox_key, bbox=json.loads(route.bbox),
                           coords=route_coords, route_title=route.title, distance=route.distance, duration=route.duration,
                           num_pubs_found=num_pubs_found, instructions=instructions)


# Login page with FB login button
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', header=True, title='Login')


# Login method for Facebook and other OAuth
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


# After user logs in on Facebook/OAuth, this brings them back to the app
@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id = oauth.callback()
    if social_id is None:
        flash('Authentication failed.', 'danger')
        return redirect(url_for('homepage'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete. Thanks for joining!', 'success')
    else:
        flash('Welcome back!', 'success')
    login_user(user, True)
    return redirect(url_for('homepage'))


# Logout button
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/saveroute', methods=['GET'])
@login_required
def save_route():
    unsaved_route_id = session.get('unsaved_route_id')

    if unsaved_route_id:
        route = Route.query.get(unsaved_route_id)
        route.user_id = current_user.id
        db.session.commit()
        flash("Route saved.", 'success')
        return redirect(url_for('saved_route', route_id=unsaved_route_id))
    else:
        return redirect(url_for('saved'))


@app.route('/editroute/<route_id>', methods=['POST'])
@login_required
def edit_route(route_id):
    # Load the Route from DB, and check the corresponding user_id matches the currently logged in user
    route = Route.query.get(route_id)

    if current_user.id == route.user_id:
        new_title = request.form['title']
        if route.title != new_title:  # Check title changed before updating DB
            route.title = new_title
            db.session.commit()

    return redirect(url_for('saved_route', route_id=route_id))


@app.route('/saved')
@login_required
def saved():
    own_routes = list(Route.query.filter_by(user_id=current_user.id).order_by(Route.timestamp.desc()))
    all_routes = list(Route.query.filter().order_by(Route.timestamp.desc()))

    return render_template('allroutes.html', header=True, title='Saved Routes', own_routes=own_routes, all_routes=all_routes)


@app.route('/route/<route_id>')
def saved_route(route_id):
    if current_user.is_anonymous:
        flash('To view saved routes, you will need to first sign in.', 'warning')
        return redirect(url_for('login'))

    route = Route.query.filter_by(id=route_id).first_or_404()

    if not route.title:
        route.title = "Untitled Route"

    route_coords = routefinder.polyline_to_coords(route.polyline)

    return render_template('route.html', header=False, title='View Route #{}'.format(route.id), mapbox_key=mapbox_key, route=route,
                           bbox=json.loads(route.bbox), coords=route_coords, distance=route.distance, duration=route.duration)
