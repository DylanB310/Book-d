from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField
from wtforms import validators
from wtforms.fields.core import RadioField
from wtforms.validators import DataRequired
from wtforms.widgets.core import CheckboxInput
from app.models import Courses, Departments, Professors
from app import db

class AddMediaForm(FlaskForm):
    copies = StringField('Copies Offered:', validators=[DataRequired()])
    title = StringField('Title:', validators=[DataRequired()])
    author = StringField('Author:')
    category = RadioField('Genre:',  
                    choices = [('ACD','Academic'),('ENT','Entertainment'),('REF','Reference')], 
                    validators=[DataRequired()])
    department = SelectField('Department', choices=[], validators=[DataRequired()])
    professor = SelectField('Professor', choices=[], validators=[DataRequired()])
    course = SelectField('Course:',choices=[], validators=[DataRequired()])
    media_type = RadioField('Media Type', choices = [('P','Print'),('A','Audio'),('V','Video')], validators=[DataRequired()])
    upload = FileField('Media file', validators=[FileRequired()])
    submit = SubmitField('Add Media')
