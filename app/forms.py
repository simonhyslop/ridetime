# Handles form display and validation using the wtforms library

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange


# Location input for user to enter their start location when creating a new route
class LocationSearch(FlaskForm):
    location = StringField(render_kw={"placeholder": "Postcode / place name"}, validators=[InputRequired()])
    submit = SubmitField('Go')


# Distance input for user to set a preferred route length when creating a new route
class DistanceInput(FlaskForm):
    distance = IntegerField('Distance', validators=[NumberRange(min=1, max=100)])
    submit = SubmitField('Update')
