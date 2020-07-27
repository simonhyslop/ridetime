from datetime import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    db.relationship('Ride', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}, username {}>'.format(self.id, self.username)


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=False, unique=False)
    coordinates = db.Column(db.String(120), index=False, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Ride {}, created by user ID {} on {}'.format(self.id, self.user_id, self.timestamp)
