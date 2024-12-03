from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from flask import Blueprint

from .models.cart import Cart

bp = Blueprint('cart', __name__)

@bp.route('/cart', methods=['GET'])
@login_required
def cart():
    cartItems = Cart.get_by_user(current_user.id)
    return render_template('cart.html', cart_items=cartItems)

@bp.route('/cart/update', methods=['POST'])
@login_required
def update_item():
    cart_item_id = request.form.get('cart_item_id')
    quantity = request.form.get('quantity')

    if not cart_item_id or not quantity:
        flash('Invalid request. Please try again.', 'danger')
        return redirect(url_for('cart.cart'))

    try:
        quantity = int(quantity)
        if quantity < 1:
            flash('Quantity must be at least 1.', 'warning')
            return redirect(url_for('cart.cart'))
    except ValueError:
        flash('Invalid quantity value.', 'danger')
        return redirect(url_for('cart.cart'))

    success = Cart.update_item_quantity(cart_item_id, quantity)
    if success:
        flash('Cart updated successfully.', 'success')
    else:
        flash('Failed to update cart. Please try again.', 'danger')

    return redirect(url_for('cart.cart'))

@bp.route('/cart/remove', methods=['POST'])
@login_required
def remove_item():
    cart_item_id = request.form.get('cart_item_id')

    if not cart_item_id:
        flash('Invalid request. Please try again.', 'danger')
        return redirect(url_for('cart.cart'))

    success = Cart.remove_item(cart_item_id)
    if success:
        flash('Item removed from cart.', 'success')
    else:
        flash('Failed to remove item. Please try again.', 'danger')

    return redirect(url_for('cart.cart'))
