# Here we establish classes for different objects we require, and specify
# how these relate to DB tables/columns so that our ORM SQLAlchemy can process them.

from datetime import datetime
from app import db, lm
from flask_login import UserMixin


# User class for handling user registration and login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=True)
    routes = db.relationship('Route', backref='creator', lazy='dynamic')

    @lm.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
        return "User ID {}".format(self.id)


# Route class for storing and loading cycling routes
class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    public = db.Column(db.Boolean, index=True, default=False)
    title = db.Column(db.String(120), index=False)
    distance = db.Column(db.Integer, index=False)
    duration = db.Column(db.Integer, index=False)
    bbox = db.Column(db.String(120), index=False)
    polyline = db.Column(db.String(10000), index=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "Ride {}, created by user ID {} on {}".format(self.id, self.user_id, self.timestamp)
