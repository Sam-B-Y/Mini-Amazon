from flask import render_template, redirect, url_for, flash, request,make_response
from werkzeug.urls import url_parse
from flask import jsonify
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.review import Review

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        redirect_response = make_response(redirect(next_page))
        redirect_response.set_cookie("id", str(user.id))

        return redirect_response

    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         str.strip(form.firstname.data) + " " + str.strip(form.lastname.data),
                         form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/account', methods=['GET', 'POST'])
def view_account():
    id = int(request.cookies.get("id"))
    user = User.get(id)
    order_history = User.get_product_history(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))

    if request.method == "GET":
        return render_template('account.html', title="View Account", full_name=user.full_name, 
                email=user.email, address=user.address, balance=user.balance, order_history=order_history)
    else:
        field_id = request.form.get("form_id")
        field_value = request.form.get(field_id)
        User.update(id, field_id, field_value)
        user = User.get(id)

        return render_template('account.html', title="View Account", full_name=user.full_name, 
                email=user.email, address=user.address, balance=user.balance, order_history=order_history)
