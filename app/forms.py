from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.core import RadioField
from wtforms.validators import DataRequired

class AddMediaForm(FlaskForm):
    copies = StringField('Copies Offered:', validators=[DataRequired()])
    title = StringField('Title:', validators=[DataRequired()])
    author = StringField('Author:')
    category = RadioField('Genre:',  
                    choices = [('ACD','Academic'),('ENT','Entertainment'),('REF','Reference')], 
                    validators=[DataRequired()])
    department = SelectField('Department', choices=[])
    professor = SelectField('Professor', choices=[])
    course = SelectField('Course:',choices=[])
    media_type = RadioField('Media Type', choices = [('P','Print'),('A','Audio'),('V','Video')], validators=[DataRequired()])
    upload = FileField('Media file', validators=[
            FileAllowed(['pdf', 'mp4', 'webm', 'ogg', 'mpeg', 'wav'], 'Supports Video, PDF, Audio.'),
            FileRequired()])
    submit = SubmitField('Add Media')
