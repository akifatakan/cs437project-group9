from flask import Flask, render_template, session, redirect, url_for
from forms import SignUpForm, LoginForm


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    form = SignUpForm()
    if form.validate_on_submit():
        # Add your sign-up logic here, e.g., save user to database
        # For simplicity, let's just print the form data for now
        print(f"Sign Up Form Submitted: {form.data}")
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        # Add your login logic here, e.g., check user credentials
        # For simplicity, let's just print the form data for now
        print(f"Login Form Submitted: {form.data}")
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)