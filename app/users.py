from flask import render_template, redirect, url_for, flash, request, make_response
from werkzeug.urls import url_parse
from flask import jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from hashlib import sha256
from flask import abort

from .models.user import User
from .models.review import Review
from .forms.inventory_form import InventoryForm

from flask import Blueprint
bp = Blueprint('users', __name__)

class UserInfoForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    balance = StringField('Balance', validators=[DataRequired()])
    submit = SubmitField('Update')

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
    redirect_response = make_response(redirect(url_for('index.index')))
    redirect_response.set_cookie("id", "", expires=0)
    return redirect_response


@bp.route('/add_funds', methods=['POST'])
@login_required
def add_funds():
    id = current_user.id
    user = User.get(id)
    
    if user is None:
        return jsonify({"error": "User not found"}), 404

    amount = float(request.form['amount'])
    if amount <= 0:
        flash(f"Invalid amount.", "danger")
        return redirect(url_for('users.edit_account'))

    user.balance = float(user.balance) + amount
    user.save(user)
    flash(f"Successfully added ${amount:.2f} to your account.", "success")
    return redirect(url_for('users.edit_account'))

@bp.route('/withdraw_funds', methods=['POST'])
@login_required
def withdraw_funds():
    id = current_user.id
    user = User.get(id)

    user.balance = float(user.balance)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    amount = float(request.form['amount'])
    if amount <= 0:
        flash(f"Invalid amount.", "danger")
        return redirect(url_for('users.edit_account'))

    if amount > user.balance:
        flash(f"Insufficient funds.", "danger")
        return redirect(url_for('users.edit_account'))

    user.balance -= amount
    user.save(user)
    flash(f"Successfully withdrew ${amount:.2f} from your account.", "success")
    return redirect(url_for('users.edit_account'))

@bp.route('/edit_account', methods=['GET', 'POST'])
@login_required
def edit_account():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        form_id = request.form.get('form_id')
        if form_id == 'full_name':
            full_name = request.form.get('full_name', '').strip()
            if full_name:
                user.full_name = full_name
                user.save(user)
                flash("Full Name updated successfully.", "success")
            else:
                flash("Invalid full name provided.", "danger")
        elif form_id == 'address':
            address = request.form.get('address', '').strip()
            if address:
                user.address = address
                user.save(user)
                flash("Address updated successfully.", "success")
            else:
                flash("Invalid address provided.", "danger")
        else:
            flash("Unknown form submitted.", "danger")
        return redirect(url_for('users.edit_account'))

    return render_template('account/edit_account.html', 
                           title='Edit Account', 
                           full_name=user.full_name, 
                           address=user.address, 
                           balance=user.balance, 
                           email=user.email)

@bp.route('/purchase_history', methods=['GET'])
@login_required
def purchase_history():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))
    
    page = request.args.get("page", default=1, type=int)
    per_page = 10

    order_history_data = User.get_product_history(id, page=page, per_page=per_page)
    order_history = order_history_data["rows"]
    total_pages = order_history_data["pages"]

    return render_template('account/purchases.html', title="Purchase History", order_history=order_history, page=page, total_pages=total_pages)

@bp.route('/become_seller', methods=['GET'])
@login_required
def become_seller():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))

    User.become_seller(id)
    flash("You are now a seller!", "success")
    
    return redirect(url_for('users.view_account'))

@bp.route('/seller_profile', methods=['GET'])
@login_required
def seller_profile():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))

    is_seller = User.is_seller(id)
    if not is_seller:
        # alert user that they are not a seller
        flash("Cannot open page - you are not a seller.", "danger")
        return redirect(url_for('users.view_account'))
    
    stats = User.get_seller_stats(id)
    print(stats)

    return render_template('seller/main.html', title="Seller Profile", seller_stats=stats)

@bp.route('/view_orders', methods=['GET'])
@login_required
def view_orders():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))
    
    is_seller = User.is_seller(id)
    if not is_seller:
        return redirect(url_for('users.view_account'))

    return render_template('seller/orders.html', title="View Orders")

@bp.route('/view_inventory', methods=['GET'])
@login_required
def view_inventory():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))
    
    is_seller = User.is_seller(id)
    if not is_seller:
        return redirect(url_for('users.view_account'))
    

    return render_template('seller/inventory.html', title="View Inventory")


@bp.route('/account', methods=['GET'])
@login_required
def view_account():
    id = current_user.id
    user = User.get(id)

    if user is None:
        logout_user()
        return redirect(url_for('users.login'))
    
    is_seller = User.is_seller(id)
    return render_template('account/main.html', title="View Account", is_seller=is_seller)

  
@bp.route('/user/<hashed_email>')
def view_user(hashed_email):
    users = User.get_all()
    found_user = None
    
    for user in users:
        user_hash = sha256(user.email.encode()).hexdigest()
        if user_hash == hashed_email:
            found_user = user
            break
    
    if not found_user:
        abort(404)

    is_seller = User.is_seller(found_user.id)
        
    if not is_seller:
        return render_template('view_user.html', 
                         full_name=found_user.full_name,
                         email=found_user.email,
                         seller_id=found_user.id)

    ratings = Review.get_seller_reviews(found_user.id)

    if ratings:
        total_rating = sum(review.rating for review in ratings)
        average_rating = total_rating / len(ratings)
    else:
        average_rating = 0

    return render_template('view_seller.html', 
                         full_name=found_user.full_name,
                         email=found_user.email,
                         seller_id=found_user.id, reviews=ratings, address=found_user.address, average_rating=average_rating)

@bp.route('/api/user/<int:user_id>/email')
def get_user_email(user_id):
    email = User.get_email_from_id(user_id)
    if not email:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'email': email})
