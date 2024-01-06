# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from .models import User


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please enter a username.")])
    email = StringField('Email', validators=[DataRequired(message="Please enter your email address."),
                                             Email(message="Invalid email address.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter a password.")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(message="Please confirm your password."),
                                                 EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if User.query.filter_by(email=self.email.data).first():
            raise ValidationError('Email has been registered')

    def validate_username(self, username):
        if User.query.filter_by(username=self.username.data).first():
            raise ValidationError('Username has been registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Please enter your email address."),
                                             Email(message="Invalid email address.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter your password.")])
    submit = SubmitField('Log In')


class ChangeRoleForm(FlaskForm):
    submit = SubmitField('Change Role')


class SearchNewsForm(FlaskForm):
    search_query = StringField('Search News')
    submit = SubmitField('Search')


class SearchUsersForm(FlaskForm):
    search_query = StringField('Search News')
    submit = SubmitField('Search')


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')


class DeleteCommentForm(FlaskForm):
    submit = SubmitField('Delete Comment')


class DeleteUserForm(FlaskForm):
    submit = SubmitField("Delete User")


class SearchUserForm(FlaskForm):
    search_term = StringField('Search by User ID or Username')
    submit = SubmitField('Search')


class FollowFriendForm(FlaskForm):
    submit = SubmitField('Follow')


class UnfollowFriendForm(FlaskForm):
    submit = SubmitField('Unfollow')