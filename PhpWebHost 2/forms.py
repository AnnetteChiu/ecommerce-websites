from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ContentForm(FlaskForm):
    """Form for creating new content"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        Length(min=1, max=10000, message='Content must be between 1 and 10000 characters')
    ])
    
    category = SelectField('Category', validators=[DataRequired(message='Category is required')])
    
    status = SelectField('Status', validators=[DataRequired(message='Status is required')])
    
    author = StringField('Author', validators=[
        DataRequired(message='Author is required'),
        Length(min=1, max=100, message='Author must be between 1 and 100 characters')
    ])
    
    tags = StringField('Tags', validators=[
        Length(max=500, message='Tags must be less than 500 characters')
    ], description='Separate tags with commas')
    
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'], 'Only image files are allowed!')
    ], description='Upload an image (JPG, PNG, GIF, WEBP, SVG)')
    
    submit = SubmitField('Create Content')

class EditContentForm(FlaskForm):
    """Form for editing existing content"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        Length(min=1, max=10000, message='Content must be between 1 and 10000 characters')
    ])
    
    category = SelectField('Category', validators=[DataRequired(message='Category is required')])
    
    status = SelectField('Status', validators=[DataRequired(message='Status is required')])
    
    author = StringField('Author', validators=[
        DataRequired(message='Author is required'),
        Length(min=1, max=100, message='Author must be between 1 and 100 characters')
    ])
    
    tags = StringField('Tags', validators=[
        Length(max=500, message='Tags must be less than 500 characters')
    ], description='Separate tags with commas')
    
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'], 'Only image files are allowed!')
    ], description='Upload a new image (JPG, PNG, GIF, WEBP, SVG) - leave empty to keep current image')
    
    submit = SubmitField('Update Content')
