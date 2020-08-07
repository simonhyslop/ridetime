# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class LocationSearch(FlaskForm):
    location = StringField(default='Enter postcode or place name', validators=[InputRequired()])
    submit = SubmitField('Go')


class DistanceInput(FlaskForm):
    distance = IntegerField('Distance', validators=[NumberRange(min=1, max=100)])
    submit = SubmitField('Update')
