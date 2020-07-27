# http://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/getting-started-with-flask.html
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
# https://getbootstrap.com/docs/4.5/getting-started/introduction/
# https://docs.mapbox.com/mapbox-gl-js/api/

from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, LocationSearch
from app import datafeeds
from config import Config


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LocationSearch()
    if form.validate_on_submit():
        flash('You searched for {}'.format(form.location.data), 'info')
        coords = datafeeds.postcode_lookup(form.location.data)
        return redirect('/create?long={}&lat={}'.format(coords[0], coords[1]))

    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data), 'info')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)


@app.route('/create')
def create_route():
    mapbox_key = Config.MAPBOX_KEY  # Read Mapbox key from config file

    long = request.args.get('long')
    lat = request.args.get('lat')

    if long and lat:
        start_coords = long, lat
    else:
        start_coords = -1.930556, 52.450556  # If no location provided, default to UoB

    # route = datafeeds.route_to_london(start_coords)
    return render_template('create.html', title='New route', mapbox_key=mapbox_key, start=start_coords)
