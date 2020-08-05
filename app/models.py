from datetime import datetime
from app import db, lm
from flask_login import UserMixin


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
        return '<User {}, nickname: {}>'.format(self.user_id, self.nickname)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120), index=False, unique=False)
    coordinates = db.Column(db.String(120), index=False, unique=False)
    gpx = db.Column(db.String(120), index=False, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return 'Ride {}, created by user ID {} on {}'.format(self.id, self.user_id, self.timestamp)
