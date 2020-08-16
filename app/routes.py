import json
from flask import render_template, flash, redirect, url_for, request, session, Response
from app import app, db, routefinder
from app.forms import LocationSearch
from config import Config
from flask_login import login_user, logout_user, current_user, login_required
from slugify import slugify
from app.oauth import OAuthSignIn
from app.models import User, Route
from app.datafeeds import postcode_lookup, polyline_to_coords
from app.gpx import route_to_gpx

mapbox_key = Config.MAPBOX_KEY  # Read Mapbox key from config file


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def homepage(header=True):
    form = LocationSearch()
    if form.validate_on_submit():  # When user submits their location, look it up using ORS API
        result_found, coords, address = postcode_lookup(form.location.data)
        if result_found:  # If a matching location is found, move to next page
            session['start_location'] = address
            session['start_coords'] = coords
            # flash("Location found: {}".format(address), 'info')  TODO: debugging
            return render_template('index.html', header=False, location_input=form, mapbox_key=mapbox_key,
                                   start=coords)
        else:  # If no location found, show an error
            flash("Location '{}' not found".format(form.location.data), 'danger')

    return render_template('index.html', header=header, no_location=True, location_input=form,
                           mapbox_key=mapbox_key, start=None)


# Same view as homepage, but with intro header hidden (header:False)
@app.route('/start', methods=['GET', 'POST'])
def start_page():
    return homepage(False)


@app.route('/createroute', methods=['POST'])
def create_route():
    start_coords = request.form['startCoordinates']
    distance_requested = request.form['distanceRequested']

    # TODO:
    # Generate route using ORS
    # Save route to DB
    # Return to page as JSON

    return redirect(url_for('start_page'))


@app.route('/route')
def generate_route():
    start_coords = session.get('start_coords')

    # In case we reach this page without coordinates set, use default location of Uni Birmingham campus
    if not start_coords:
        flash("Location auto-set to Birmingham!", 'danger')
        start_coords = [-1.930556, 52.450556]  # Coordinates for Uni Birmingham campus

    # User requested distance (in km) for how far they want to cycle
    distance_requested = int(request.args.get('dist'))

    # Catch where no distance provided, or value out of range, and set value to 20
    if not distance_requested or distance_requested < 1 or distance_requested > 100:
        distance_requested = 20

    route = routefinder.ors_roundroute(start_coords, distance_requested)

    address = session.get('start_location')
    if address:
        route.title = "Route near {}".format(address)

    # Storing Route to DB without user_id set
    db.session.add(route)
    db.session.commit()

    session['unsaved_route_id'] = route.id  # Store the Route ID so that we can later assign it to a user

    route_coords = polyline_to_coords(route.polyline)

    return render_template('create.html', header=False, title='View Route', mapbox_key=mapbox_key,
                           route=route, coords=route_coords)


@app.route('/about')
def about():
    return render_template('about.html', header=True, title='About')


# Login page with FB login button
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', header=True, title='Login')


# Used where user wants to save a route, but needs to log in first
@app.route('/loginsaveroute')
def login_then_save_route():
    session['save_route'] = True  # Set flag for login method
    return redirect(url_for('oauth_authorize', provider='facebook'))


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
        flash('Login failed', 'danger')
        return redirect(url_for('homepage'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)

    # Direct user to the appropriate page after logging in
    if session.get('save_route', False):  # If user is logging in to save a route, direct them to that page
        return redirect(url_for('save_route'))
    else:  # Else if standard login, go to their view of all saved routes
        return redirect(url_for('saved'))


# Logout button
@app.route("/logout")
@login_required
def logout():
    logout_user()
    # flash("You are now logged out", 'primary')  TODO: debugging
    return redirect(url_for('homepage'))


@app.route('/saveroute', methods=['GET'])
@login_required
def save_route():
    unsaved_route_id = session.get('unsaved_route_id')

    if unsaved_route_id:
        route = Route.query.get(unsaved_route_id)
        route.user_id = current_user.id
        db.session.commit()
        session['save_route'] = False  # Clear flag for login method
        flash('Route saved', 'success')
        return redirect(url_for('view_route', route_id=unsaved_route_id))
    else:
        return redirect(url_for('saved'))


@app.route('/editroute/<route_id>', methods=['POST'])
@login_required
def edit_route(route_id):
    # Load the Route from DB, and check the corresponding user_id matches the currently logged in user
    route = Route.query.get(route_id)

    if current_user.id == route.user_id:  # Only edit if route belongs to the logged-in user
        new_title = request.form['title']
        new_public = json.loads(request.form['isPublic'])
        if route.title != new_title or route.public != new_public:  # Only update if changes made
            route.title = new_title
            route.public = new_public
            db.session.commit()

    return redirect(url_for('view_route', route_id=route_id))


@app.route('/saved')
@login_required
def saved():
    own_routes = list(Route.query.filter_by(user_id=current_user.id).order_by(Route.timestamp.desc()))
    all_routes = list(
        Route.query.filter(Route.public, Route.user_id != current_user.id).order_by(
            Route.timestamp.desc()).all())

    return render_template('allroutes.html', header=False, title='Saved Routes', own_routes=own_routes,
                           all_routes=all_routes)


@app.route('/route/<int:route_id>')
def view_route(route_id):
    route = Route.query.filter_by(id=route_id).first_or_404()

    if not route.public:  # If route is not public, check user has permission before allowing access
        if current_user.is_anonymous:  # Must sign in before viewing non-public routes
            flash('Sign in required', 'warning')
            return redirect(url_for('login'))

        if current_user.id != route.user_id:  # Must be route owner in order to view it  # TODO: Allow sharing with other users
            flash('This route is not shared with you', 'warning')
            return redirect(url_for('saved'))

    # If we get here: route is either public, or user has permission to view, so we display it
    route_coords = polyline_to_coords(route.polyline)

    own_route = current_user.id == route.user_id

    return render_template('route.html', header=False, mapbox_key=mapbox_key, route=route, coords=route_coords,
                           own_route=own_route)


# Adapted from: https://stackoverflow.com/questions/28011341/create-and-download-a-csv-file-from-a-flask-view
@app.route('/gpx/<int:route_id>')
@login_required
def download_gpx(route_id):
    # TODO: Check user has permission before allowing access

    route = Route.query.filter_by(id=route_id).first_or_404()
    route_gpx = route_to_gpx(route)

    # Create a response and set the file content type
    response = Response(route_gpx, mimetype='application/gpx+xml')

    # Remove whitespace/symbols from route title, set as filename
    safe_filename = "{}.gpx".format(slugify(route.title))
    response.headers.set("Content-Disposition", "attachment", filename=safe_filename)
    return response
