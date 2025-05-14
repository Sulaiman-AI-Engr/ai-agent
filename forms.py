from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, TelField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from models import Business

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    business_type = SelectField('Business Type', choices=[
        ('clinic', 'Medical Clinic'),
        ('retail', 'Retail Store'),
        ('salon', 'Beauty Salon'),
        ('restaurant', 'Restaurant'),
        ('office', 'Office'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    phone = TelField('Phone Number', validators=[Optional(), Length(max=20)])
    address = StringField('Business Address', validators=[Optional(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if Business.query.filter_by(email=email.data).first():
            raise ValueError('That email is already registered. Please choose a different one.')

class ProfileForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=100)])
    business_type = SelectField('Business Type', choices=[
        ('clinic', 'Medical Clinic'),
        ('retail', 'Retail Store'),
        ('salon', 'Beauty Salon'),
        ('restaurant', 'Restaurant'),
        ('office', 'Office'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    phone = TelField('Phone Number', validators=[Optional(), Length(max=20)])
    address = StringField('Business Address', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ChatbotForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')