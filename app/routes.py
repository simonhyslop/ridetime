# Here we handle requests to the web server, covering the various
# endpoints, which essentially represent URL locations.
#
# Flask provides the logic for serving the pages, however the methods
# here determine the outcome of different endpoints of the site.
#
# The default method is the 'GET' request, which typically returns an HTML
# page, but can be used to trigger other events.
#
# Some endpoints accept 'POST' requests, and these allow the client to send
# a body with the request containing e.g. form data.
#
# Each method has a brief explanation of how it is implemented.

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


# Serves the website homepage, both on the base '/' and '/index' URLs.
#
# Also handles POST requests, which are received when the user inputs the
# start location for a cycling route on the webpage.
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def homepage(header=True):  # Can be called with parameter 'False' for page to load with header hidden
    form = LocationSearch()
    if form.validate_on_submit():  # Handle form submission (containing start location)
        result_found, coords, address = postcode_lookup(form.location.data)  # Look up location using ORS API
        if result_found:  # If a matching location is found, move to next page
            session['start_location'] = address  # Store location input in the cookie
            session['start_coords'] = coords  # Store corresponding coordinates in the cookie
            return render_template('index.html', header=False, location_input=form, mapbox_key=mapbox_key,
                                   start=coords)  # Reload the homepage, updating the map view to the user's location
        else:  # If no location found, display an error
            flash("Location '{}' not found".format(form.location.data), 'danger')

    # Default case for loading page before location input. Uses the template 'index.html', passes the
    # location input form, and the Mapbox key required to display a map
    return render_template('index.html', header=header, no_location=True, location_input=form,
                           mapbox_key=mapbox_key, start=None)


# Same view as homepage, but with intro header hidden (header:False)
@app.route('/start', methods=['GET', 'POST'])
def start_page():
    return homepage(False)


# This is called when the user clicks 'Continue' on the homepage,
# after entering start location and route length.
@app.route('/route')
def generate_route():
    start_coords = session.get('start_coords')  # Fetch start location coordinates from the cookie

    # In case user reaches this page without coordinates set, fallback location of Uni Birmingham campus
    if not start_coords:
        flash("Location auto-set to Birmingham!", 'danger')  # Display error to user
        start_coords = [-1.930556, 52.450556]  # Coordinates for Uni Birmingham campus

    # From the URL, retrieve the requested distance (in km) for how far
    # the user wants to cycle (URL ends /route?dist=20)
    distance_requested = request.args.get('dist', 20)

    # Convert to int, unless invalid input where we set a default value
    try:
        distance_requested = int(distance_requested)
    except ValueError:
        distance_requested = 20

    # Catch where no distance provided, or value out of range (has to be 1-100km), and set a default value
    if not distance_requested or distance_requested < 1 or distance_requested > 100:
        distance_requested = 20

    # Call the ORS API, passing the parameters for our route, and store the response
    route = routefinder.ors_roundroute(start_coords, distance_requested)

    address = session.get('start_location')  # Fetch start location name (e.g. 'Birmingham') from the user's cookie
    if address:
        route.title = "Route near {}".format(address)  # If name found, title the route (e.g. 'Route near Birmingham')

    # Storing Route to DB without user_id set
    db.session.add(route)
    db.session.commit()

    # By storing the route to DB, a route ID has been created. We store this in the user's cookie
    # so that we can locate the route, should they choose to save it to their account
    session['unsaved_route_id'] = route.id

    route_coords = polyline_to_coords(route.polyline)  # Convert route coordinates from polyline to coordinate list

    # Load the page, using the template 'create.html', passing the Mapbox key along with the
    # Route object and a list of the route coordinates
    return render_template('create.html', header=False, title='View Route', mapbox_key=mapbox_key,
                           route=route, coords=route_coords)


# Loads the 'About' page using 'about.html'
@app.route('/about')
def about():
    return render_template('about.html', header=True, title='About')


# Login page with Facebook login button to launch OAuth login process
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', header=True, title='Login')


# Used where user wants to save a route, but needs to log in first
@app.route('/loginsaveroute')
def login_then_save_route():
    session['save_route'] = True  # Set flag for login method
    return redirect(url_for('oauth_authorize', provider='facebook'))


# Login method for Facebook, extensible to support other OAuth
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    # If user is already signed in, redirect them to the home page
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


# After user logs in on Facebook/OAuth, this brings them back to the app,
# (on first visit) logs their details, and updates their status to logged in
@app.route('/callback/<provider>')
def oauth_callback(provider):
    # If user is already signed in before this process, redirect them to the home page
    if not current_user.is_anonymous:
        return redirect(url_for('homepage'))

    # Retrieve details from the OAuth process
    oauth = OAuthSignIn.get_provider(provider)
    social_id = oauth.callback()
    if social_id is None:  # OAuth provider does not pass user details (invalid login, or user cancelled process)
        flash('Login failed', 'danger')  # Display error to user
        return redirect(url_for('homepage'))  # Redirect user to the home page

    user = User.query.filter_by(social_id=social_id).first()  # Search DB to see if this user already exists
    if not user:  # If not then add them to DB
        user = User(social_id=social_id)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)  # Update user status to logged in (using flask_login library)

    # Direct user to the appropriate page after logging in
    if session.get('save_route', False):  # If user is logging in to save a route, direct them to that page
        return redirect(url_for('save_route'))
    else:  # Else if standard login, go to their view of all saved routes
        return redirect(url_for('saved'))


# Logout button
@app.route("/logout")
@login_required  # User must be logged in to proceed
def logout():
    logout_user()  # Update user status to logged out (using flask_login library)
    return redirect(url_for('homepage'))  # Redirect user to the home page


# This is called when the user has created a route and clicks the 'Save' button
@app.route('/saveroute', methods=['GET'])
@login_required  # User must be logged in to proceed
def save_route():
    unsaved_route_id = session.get('unsaved_route_id')  # Fetch the route ID from the user's cookie

    if unsaved_route_id:  # If a route ID is found, save that route to the user's account
        route = Route.query.get(unsaved_route_id)  # Locate the corresponding route in DB
        route.user_id = current_user.id  # Update the 'user_id' for that record to the current user
        db.session.commit()  # Commit changes to DB
        session['save_route'] = False  # Clear flag for login method
        flash('Route saved', 'success')  # Display confirmation to user
        return redirect(url_for('view_route', route_id=unsaved_route_id))  # Redirect user to the newly-saved route
    else:  # Otherwise if no route ID found, redirect user to a list of their saved routes
        return redirect(url_for('saved'))


# This handles edits made to a saved route, i.e. renaming and changing public/private status.
# These are received as a 'POST' request containing JSON.
@app.route('/editroute/<route_id>', methods=['POST'])
@login_required  # User must be logged in to proceed
def edit_route(route_id):
    # Load the Route from DB, and check the corresponding user_id matches the currently logged in user
    route = Route.query.get(route_id)

    if current_user.id == route.user_id:  # Only edit if route belongs to the logged-in user
        new_title = request.form['title']  # Retrieve route title from JSON
        new_public = json.loads(request.form['isPublic'])  # Retrieve public/private status from JSON
        if route.title != new_title or route.public != new_public:  # Only update if changes made
            route.title = new_title  # Update title in DB record
            route.public = new_public  # Update public/private status in DB record
            db.session.commit()  # Commit changes to DB

    # Redirect user to the newly-saved route
    return redirect(url_for('view_route', route_id=route_id))


# Allows the user to view a list of routes they have saved, and routes others have shared
@app.route('/saved')
@login_required  # User must be logged in to proceed
def saved():
    # Query DB for a list of all routes created by this user, newest first
    own_routes = list(Route.query.filter_by(user_id=current_user.id).order_by(Route.timestamp.desc()))

    # Query DB for a list of all public routes created by other users, newest first
    all_routes = list(
        Route.query.filter(Route.public, Route.user_id != current_user.id).order_by(
            Route.timestamp.desc()).all())

    # Load the page using the 'allroutes.html' template, passing in the DB results for this
    # user's routes and other users' routes
    return render_template('allroutes.html', header=False, title='Saved Routes', own_routes=own_routes,
                           all_routes=all_routes)


# Loads a specific route with map display
@app.route('/route/<int:route_id>')
def view_route(route_id):  # Pass in the route_id from the end of the URL (e.g. /route/23)
    route = Route.query.filter_by(id=route_id).first_or_404()  # Load route from DB, return error if not found

    if not route.public:  # If route is not public, check user has permission before allowing access
        if current_user.is_anonymous:  # Must sign in before viewing non-public routes
            flash('Sign in required', 'warning')  # Display warning to user
            return redirect(url_for('login'))  # Redirect user to the login page

        if current_user.id != route.user_id:  # Must be route owner in order to view it
            flash('This route is not shared with you', 'warning')  # Display error to user
            return redirect(url_for('saved'))  # Redirect user to a list of their saved routes

    # If we get here: route is either public, or user has permission to view, so we display it
    route_coords = polyline_to_coords(route.polyline)  # Convert route coordinates from polyline to coordinate list

    # We use an 'own_route' boolean so that the page template can adapt to whether the route
    # belongs to the current user or a different user
    if current_user.is_anonymous:  # If user not logged in, set to False
        own_route = False
    else:  # Else, evaluate whether current user matches route owner and return True/False
        own_route = current_user.id == route.user_id

    # Loads the page using the 'route.html' template, passing the Mapbox key, along with the Route
    # object, a list of the route coordinates, and the boolean of whether current user is route owner.
    return render_template('route.html', header=False, mapbox_key=mapbox_key, route=route, coords=route_coords,
                           own_route=own_route)


# This is called where the user clicks the 'Download GPX' button on a route page. It loads the
# requested route, converts it to GPX format (for use with bike GPS devices) and serves it
# as a file for the user to download.
#
# Adapted from: https://stackoverflow.com/questions/28011341/create-and-download-a-csv-file-from-a-flask-view
@app.route('/gpx/<int:route_id>')
@login_required  # User must be logged in to proceed
def download_gpx(route_id):

    route = Route.query.filter_by(id=route_id).first_or_404()  # Load route from DB, return error if not found
    route_gpx = route_to_gpx(route)  # Call the method from gpx.py to convert the Route object into a GPX file

    # Create a response and set the file content type
    response = Response(route_gpx, mimetype='application/gpx+xml')

    # Remove whitespace/symbols from route title using the 'slugify' library, set that as filename
    safe_filename = "{}.gpx".format(slugify(route.title))
    response.headers.set("Content-Disposition", "attachment", filename=safe_filename)
    return response
