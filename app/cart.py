from flask import render_template, redirect, url_for
from flask_login import current_user


from flask import Blueprint

from .models.cart import Cart

bp = Blueprint('cart', __name__)

@bp.route('/cart', methods=['GET'])
def cart():
    if current_user.is_authenticated:
        cartItems = Cart.get_by_user(
            current_user.id)
        return render_template('cart.html', cart_items=cartItems)
    return redirect(url_for('users.login'))


