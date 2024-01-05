# app.py
from myproject import app, db
from sqlalchemy import create_engine, text

from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from myproject.models import User, News
from myproject.forms import SignUpForm, LoginForm, ChangeRoleForm, SearchNewsForm, SearchUsersForm
from myproject.auth_config import admin_required



engine = create_engine("mysql+pymysql://cs437:cs437project@localhost/cs437_finance_db")


@app.route('/admin', methods=["GET", "POST"])
@login_required
@admin_required
def admin_page():
    users = User.query.all()
    form = ChangeRoleForm()
    search_form = SearchUsersForm()

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
        return render_template('admin.html', users=users, form=form, search_form=search_form)

    return render_template('admin.html', users=users, form=form, search_form=search_form)


@app.route('/', methods=['GET', 'POST'])
def index():

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
        return render_template('index.html', entries=entries, form = form)

    entries = News.query.all()
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
            if next == None or not next[0] == '/':
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


if __name__ == '__main__':
    app.run(debug=True)
