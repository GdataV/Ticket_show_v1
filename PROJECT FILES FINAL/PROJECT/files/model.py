from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    password = db.Column(db.String(80), nullable = False)
    is_admin = db.Column(db.Boolean,default = False )
    bookings = db.relationship('Bookings', backref = 'bookings',cascade = "delete, merge, save-update")

class Venue(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    Name = db.Column(db.String(100))
    Place = db.Column(db.String(100))
    Capacity = db.Column(db.Integer)
    Shows = db.relationship('Show', backref = 'shows',cascade = "delete, merge, save-update")

class Show(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    Name = db.Column(db.String(100),nullable = False)
    Rating = db.Column(db.Integer,nullable = True, default = 0)
    Tags = db.Column(db.String(100),nullable = True)
    Ticket_price = db.Column(db.Integer,nullable = False)
    Booked = db.Column(db.Integer,default = 0)
    starttime = db.Column(db.Integer)
    endtime = db.Column(db.Integer)
    Venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'),nullable = False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)


class Bookings(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    Tickets = db.Column(db.Integer,nullable = False)
    Name = db.Column(db.String(100),nullable = False)
    Rating = db.Column(db.Integer,nullable = False, default = 0)
    Ticket_price = db.Column(db.Integer,nullable = False)
    Venue_id = db.Column(db.Integer,nullable = False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)
