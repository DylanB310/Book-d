from enum import unique
from sqlalchemy.orm import backref
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
    rentals = db.relationship('Rentals', backref='users', lazy=True)
    reservations = db.relationship('Reservations', backref='users', lazy=True)
    
    # representation, output
    def __repr__(self):
        return self.email

class Media(db.Model):
    __tablename__ = 'media'
    # attributes for media
    media_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    media_key = db.Column(db.String(128), unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(128), nullable=True)
    category = db.Column(db.String(128), nullable=True)
    prof_id = db.Column(db.Integer, db.ForeignKey('professors.prof_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'), nullable=False)
    rentals = db.relationship('Rentals', backref='media', lazy=True)
    reservations = db.relationship('Reservations', backref='media', lazy=True)

    def __repr__(self):
        return self.media_key

class Rentals(db.Model):
    __tablename__ = 'rentals'
    # attributes for rental
    rental_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.media_id'), nullable=False)
    email = db.Column(db.String(128), db.ForeignKey('users.email'), nullable=False)
    date_rented = db.Column(db.DateTime, nullable=False)
    date_returned = db.Column(db.DateTime, nullable=False)
    checked_in = db.Column(db.Boolean, nullable=False)

    def __repr__(self): 
        return self.rental_id

class Reservations(db.Model):
    __tablename__ = 'reservations'
    # attributes
    res_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.media_id'), nullable=False)
    email = db.Column(db.String(128), db.ForeignKey('users.email'), nullable=False)
    res_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return self.res_id

class Departments(db.Model):
    __tablename__ = 'departments'
    # attr
    dept_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    dept_name = db.Column(db.String(128), nullable=False)
    teachers = db.relationship('Professors', backref='departments', lazy=True)
    courses = db.relationship('Courses', backref='departments', lazy=True)
    media = db.relationship('Media', backref='departments', lazy=True)

    def __repr__(self):
        return self.dept_id

class Professors(db.Model):
    __tablename__ = 'professors'
    # attr
    prof_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'), nullable=False)
    courses = db.relationship('Courses', backref='professors', lazy=True)
    media = db.relationship('Media', backref='professors', lazy=True)

    def __repr__(self) -> str:
        return self.prof_id

class Courses(db.Model):
    __tablename__ = 'courses'
    # attr
    course_id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    course_name = db.Column(db.String(128))
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'), nullable=False)
    prof_id = db.Column(db.Integer, db.ForeignKey('professors.prof_id'), nullable=False)
    media = db.relationship('Media', backref='courses', lazy=True)

    def __repr__(self) -> str:
        return self.course_id
