
from app import db

class Users(db.Model):
    # db engine inheritance from app
    __tablename__ = 'users'
    # create attributes for Users class
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    role = db.Column(db.String(32), nullable=False)
    blocked = db.Column(db.Boolean, nullable=False)
    subscribed = db.Column(db.Boolean, nullable=False)
    
    # representation, output
    def __repr__(self):
        return self.email

class Rentals(db.Model):
    __tablename__ = 'rentals'
    # attributes for rental
    rental_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    rental_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    date_rented = db.Column(db.DateTime, nullable=False)
    date_returned = db.Column(db.DateTime, nullable=False)
    checked_in = db.Column(db.Boolean, nullable=False)

    def __repr__(self): 
        return self.rental_name