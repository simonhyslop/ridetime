# Contains the configuration for our app, keeping this together in one location
#
# Credentials, keys, etc. can be hardcoded here during development, but should be loaded
# from the OS environment (i.e. Heroku) during production.

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'E9AcXgcsRSHWVBYeRMPS'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAPBOX_KEY = 'pk.eyJ1Ijoic2ltb25oeXNsb3AiLCJhIjoiY2tkd3NhMHYxNDI4NDJ6cm9vdnd0aHhydCJ9.P2L5WzrKVdatkF_X-VIFeQ'
    ORS_KEY = '5b3ce3597851110001cf6248ac1d4c19bb154649ada5b45d88b397f0'
    OAUTH_CREDENTIALS = {
        'facebook': {
            'id': '298123958067448',
            'secret': 'd1b5f2a008fe00f2f03cb240b018ea34'
        }
    }
