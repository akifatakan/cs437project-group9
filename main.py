from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

class SignupForm(FlaskForm):
    username = StringField("Username:",)
    email = StringField("Email:")
    password = StringField("Password:")

    submit = SubmitField("Submit")



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():

    signupForm = SignupForm()


    if signupForm.validate_on_submit():
        session["username"] = signupForm.username.data
        session["email"] = signupForm.email.data
        session["password"] = signupForm.password.data

        return redirect(url_for("index"))

    return render_template('signup.html', signupForm=signupForm)

@app.route('/login')
def login_page():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)