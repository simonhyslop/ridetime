# Contains the configuration for our app, keeping this together in one location
#
# Credentials, keys, etc. can be hardcoded here during development, but should be loaded
# from the OS environment (i.e. Heroku) during production.

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zfdAbXF2BRLL2CneKemU'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAPBOX_KEY = os.environ.get('MAPBOX_KEY')
    ORS_KEY = os.environ.get('ORS_KEY')
    OAUTH_CREDENTIALS =  {
        'facebook': {
            'id': os.environ.get('FB_ID'),
            'secret': os.environ.get('FB_SECRET')
        }
    }
