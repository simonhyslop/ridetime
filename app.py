# http://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/getting-started-with-flask.html
# https://getbootstrap.com/docs/4.5/getting-started/introduction/
# https://docs.mapbox.com/mapbox-gl-js/api/

from flask import Flask, render_template
import datafeeds

app = Flask(__name__)


@app.route('/')  # Homepage
def homepage():
    return render_template('index.html')


@app.route('/create')
@app.route('/create/<location>')
def map_home(location=None):
    mapbox_key = open('mapbox_key').readline()  # Read Mapbox key from file

    if location:
        start_coords = datafeeds.postcode_lookup(location)
    else:
        start_coords = -1.930556, 52.450556  # If no location provided, default to UoB

    # route = datafeeds.route_to_london(start_coords)
    return render_template('create.html', mapbox_key=mapbox_key, start=start_coords)


if __name__ == '__main__':
    app.run()
