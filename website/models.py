from . import db
from sqlalchemy.sql import func


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    positivityChance = db.Column(db.String(10))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    short_breadth = db.Column(db.String(5))
    confusion = db.Column(db.String(5))
    chest_pain = db.Column(db.String(5))
    results = db.relationship('Result')
