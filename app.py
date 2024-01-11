# app.py
from fetch_news import fetch_news
from myproject import app, db
from sqlalchemy import create_engine, text

from flask import render_template, redirect, request, url_for, flash, render_template_string, abort
from flask_login import login_user, login_required, logout_user, current_user
from myproject.models import User, News, Comment, Friendship
from myproject.forms import (SignUpForm, LoginForm, DeleteUserForm, ChangeRoleForm,
                             SearchNewsForm, SearchUsersForm, CommentForm, DeleteCommentForm,
                             SearchUserForm, FollowFriendForm, UnfollowFriendForm, SearchCommentForm)
from myproject.auth_config import admin_required

engine = create_engine("mysql+pymysql://cs437:cs437project@localhost/cs437_finance_db")


@app.route('/admin', methods=["GET", "POST"])
@login_required
@admin_required
def admin_page():
    users = User.query.all()
    form = ChangeRoleForm()
    search_form = SearchUsersForm()
    delete_user_form = DeleteUserForm()

    if search_form.validate_on_submit():
        searched_text = search_form.search_query.data
        if searched_text == "":
            users = User.query.all()
        else:
            query = f"SELECT * FROM users WHERE id = {searched_text}"
            sql_expression = text(query)
            print(sql_expression)
            with engine.connect() as connection:
                result = connection.execute(sql_expression)
                users = result.fetchall()
        return render_template('admin.html', users=users, form=form,
                               search_form=search_form, delete_user_form=delete_user_form)

    return render_template('admin.html', users=users, form=form,
                           search_form=search_form, delete_user_form=delete_user_form)


@app.route('/', methods=['GET', 'POST'])
def index():
    fetch_news()
    form = SearchNewsForm()
    if form.validate_on_submit():

        searched_text = form.search_query.data
        if searched_text == "":
            entries = News.query.all()
        else:
            query = f"SELECT * FROM news WHERE title LIKE '%{searched_text}%'"
            sql_expression = text(query)
            with engine.connect() as connection:
                result = connection.execute(sql_expression)
                entries = result.fetchall()
            print(entries[0])
        return render_template('index.html', entries=entries, form=form)

    entries = News.query.order_by(News.published.desc()).all()
    return render_template('index.html', entries=entries, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('index'))


@app.route('/welcome')
@login_required
def welcome_user():
    if request.args.get('username'):
        username = request.args.get('username')
        template = f"""
        <h1> Welcome {username} </h1> 
        """
        return render_template_string(template)

    return render_template('welcome_user.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login_page'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next is None or not next[0] == '/':
                next = url_for('welcome_user')

            return redirect(next)
    return render_template('login.html', form=form)


@app.route('/change_role/<int:user_id>', methods=['POST'])
@admin_required
@login_required
def change_role(user_id):
    user = User.query.get(user_id)

    if request.method == 'POST':
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Toggled admin status for user {user.username}.', 'success')

    return redirect(url_for('admin_page'))


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('admin_page'))


@app.route('/news/<int:news_id>', methods=["GET", "POST"])
def news_details(news_id):
    # Assuming you have a model named News and a method to get details by ID
    news_entry = News.query.get(news_id)
    comments = Comment.query.filter_by(news_id=news_id).all()
    for comment in comments:
        user = User.query.get(comment.user_id)
        comment.user = user
    form = CommentForm()
    deleteCommentForm = DeleteCommentForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        comment_text = form.comment.data
        new_comment = Comment(comment=comment_text, news_id=news_entry.id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully', 'success')
        comments = Comment.query.filter_by(news_id=news_id).all()
        for comment in comments:
            user = User.query.get(comment.user_id)
            comment.user = user
        form.comment.data = ""
        redirect(url_for("news_details", news_id=news_entry.id))

    return render_template('news_details.html', news_entry=news_entry, comments=comments, form=form,
                           deleteCommentForm=deleteCommentForm)


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@admin_required
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    news_id = comment.news_id
    if request.method == 'POST':
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for("news_details", news_id=news_id))


@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    follow_form = FollowFriendForm()
    unfollow_form = UnfollowFriendForm()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))

    comments = Comment.query.filter_by(user_id=user.id).all()

    followers = Friendship.query.filter_by(following_id=user.id)

    follower_users = [User.query.get(follower.follower_id) for follower in followers]

    return render_template('user_profile.html', user=user, comments=comments,
                           follow_form=follow_form, unfollow_form=unfollow_form, followers=follower_users)


@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    form = SearchUserForm()
    users = []
    if form.validate_on_submit():
        search_term = form.search_term.data
        # Check if the search term is numeric (assuming it's a user ID)
        query = f"SELECT * FROM users WHERE username LIKE '%{search_term}%'"
        sql_expression = text(query)
        print(sql_expression)
        with engine.connect() as connection:
            result = connection.execute(sql_expression)
            users = result.fetchall()

        return render_template('search_user.html', users=users, form=form)

    return render_template('search_user.html', form=form, users=users)


@app.route('/user/<username>/followers')
def user_followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))

    followers = Friendship.query.filter_by(following_id=user.id)

    follower_users = [User.query.get(follower.follower_id) for follower in followers]

    return render_template('user_followers.html', user=user, followers=follower_users)


@app.route('/user/<username>/followings')
def user_followings(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))

    followings = Friendship.query.filter_by(follower_id=user.id)

    following_users = [User.query.get(following.following_id) for following in followings]

    return render_template('user_followings.html', user=user, followings=following_users)


@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get(user_id)
    friendship = Friendship(follower_id=current_user.id, following_id=user_id)

    if request.method == 'POST':
        db.session.add(friendship)
        db.session.commit()

    return redirect(url_for('user_profile', username=user.username))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.get(user_id)
    friendship = Friendship.query.filter_by(follower_id=current_user.id, following_id=user_id).first()

    if request.method == 'POST':
        db.session.delete(friendship)
        db.session.commit()

    return redirect(url_for('user_profile', username=user.username))


@app.route('/search_comments', methods=['POST', 'GET'])
def search_comment():
    form = SearchCommentForm()
    template = ""
    if form.validate_on_submit():
        comment_id = form.search_term.data
        comment = Comment.query.get(comment_id)
        if comment is not None:
            template = f"""
            <p> {comment.comment} </p>"""
        else:
            template = f"""
            <p> No comment found with id: {comment_id} </p>"""
        return render_template_string(template)

    return render_template('search_comment.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
