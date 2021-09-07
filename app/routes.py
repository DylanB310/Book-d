from werkzeug.utils import redirect
from app import app, db
from flask import render_template, url_for, session, flash
from flask_login import login_user, login_required, current_user
from app.forms import LoginForm
from app.models import Users

@app.route("/")
def splash():
    return render_template("base.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = db.session.query(Users).filter_by(email=email).first()

        if user is not None and password == user.password:
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@login_required
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('homepage.html')
