
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
