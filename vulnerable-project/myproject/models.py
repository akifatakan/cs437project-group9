import datetime
from myproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()


# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    subtitle = db.Column(db.String(2048))
    published = db.Column(db.DateTime)
    image_url = db.Column(db.String(256))
    details = db.Column(db.String(4096))
    link = db.Column(db.String(256))

    def __init__(self, title, subtitle, published, image_url, details, link):
        self.title = title
        self.subtitle = subtitle
        self.published = published
        self.image_url = image_url
        self.details = details[0:4095]
        self.link = link


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    comment_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, news_id, user_id, comment):
        self.news_id = news_id
        self.user_id = user_id
        self.comment = comment
        self.comment_date = datetime.datetime.now()

    def __repr__(self):
        return f'<Comment {self.id}>'


class Friendship(db.Model):

    __tablename__ = "friendships"

    id= db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, follower_id, following_id):
        self.follower_id = follower_id
        self.following_id = following_id

    def __repr__(self):
        return f'<friendship {self.id}>'
    
class Dummy(db.Model):

    __tablename__ = "dummy"
    id= db.Column(db.Integer, primary_key=True)
