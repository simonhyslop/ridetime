from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange


class LocationSearch(FlaskForm):
    location = StringField(default='Enter postcode or place name', validators=[InputRequired()])
    submit = SubmitField('Go')


class DistanceInput(FlaskForm):
    distance = IntegerField('Distance', validators=[NumberRange(min=1, max=100)])
    submit = SubmitField('Update')
