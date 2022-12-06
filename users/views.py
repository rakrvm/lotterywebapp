# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, session, Markup, request
import bcrypt, pyotp, logging
from app import db, requires_roles
from models import User
from users.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        logging.warning('SECURITY - User registration [%s, %s]', form.email.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # create signup form object
    form = LoginForm()

    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0

    if form.validate_on_submit():
        # checks user credentials
        user = User.query.filter_by(email=form.username.data).first()

        if not user or not bcrypt.checkpw(form.password.data.encode('utf-8'), user.password) or not pyotp.TOTP(
                user.pinKey).verify(form.pin.data):
            session['authentication_attempts'] += 1

            if session.get('authentication_attempts') >= 3:
                flash(Markup('Number of incorrect login attempts exceeded. Please click <a href="/reset">here</a> to '
                             'reset.'))

                return render_template('users/login.html')

            logging.warning('SECURITY - Invalid Log in attempt [%s, %s]', form.username.data, request.remote_addr)
            flash('Please check your login details and try again, {} login attempts remaining'.format(
                3 - session.get('authentication_attempts')))
            return render_template('users/login.html', form=form)

        else:
            login_user(user)
            logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)

            user.last_login = user.current_login
            user.current_login = datetime.now()

            db.session.add(user)
            db.session.commit()

            if current_user.role == 'user':
                return render_template("users/profile.html", form=form, name=current_user.firstname)
            else:
                return render_template("admin/admin.html", name=current_user.firstname)
    return render_template('users/login.html', form=form)


# log out user
@users_blueprint.route('/logout')
@login_required
def logout():
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)
    logout_user()
    return render_template('main/index.html')


# resets login limit count
@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


# view user profile
@users_blueprint.route('/profile')
@login_required
@requires_roles('user')
def profile():
    return render_template('users/profile.html', name=current_user.firstname)


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('users/account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)
