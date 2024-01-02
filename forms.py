# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please enter a username.")])
    email = StringField('Email', validators=[DataRequired(message="Please enter your email address."),
                                             Email(message="Invalid email address.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter a password.")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(message="Please confirm your password."),
                                                 EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Please enter your email address."),
                                             Email(message="Invalid email address.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter your password.")])
    submit = SubmitField('Log In')
