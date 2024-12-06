from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from flask import Blueprint

from .models.cart import Cart
from .models.coupon import Coupon

bp = Blueprint('cart', __name__)

@bp.route('/cart', methods=['GET'])
@login_required
def cart():
    cartItems = Cart.get_by_user(current_user.id)
    coupons = Coupon.get_user_available_coupons(current_user.id)
    cartCoupon = Coupon.get_cart_coupons(current_user.id)

    totalCost = 0
    for item in cartItems:
        totalCost += item.price * item.quantity
    subtotal = totalCost
    for coupon in cartCoupon:
        totalCost -= totalCost * coupon.discount / 100
    
    return render_template('cart.html', cart_items=cartItems, coupons=coupons, applied_coupons=cartCoupon, subtotal=subtotal, totalCost=totalCost)

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

@bp.route('/cart/add', methods=['POST'])
@login_required
def add_item():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    seller_id = request.form.get('seller_id')

    if not product_id or not quantity:
        flash('Invalid request. Please try again.', 'danger')
        return redirect(url_for('cart.cart'))

    try:
        product_id = int(product_id)
        quantity = int(quantity)
        if quantity < 1:
            flash('Quantity must be at least 1.', 'warning')
            return redirect(url_for('cart.cart'))
    except ValueError:
        flash('Invalid quantity value.', 'danger')
        return redirect(url_for('cart.cart'))

    success = Cart.add_item(current_user.id, product_id, seller_id, quantity)
    if success:
        flash('Item added to cart.', 'success')
    else:
        flash('Failed to add item. Please try again.', 'danger')

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


@bp.route('/cart/checkout', methods=['POST'])
@login_required
def checkout():
    success = Cart.checkout(current_user.id)
    if success == "success":
        flash('Checkout successful.', 'success')
    else:
        flash(f'Failed to checkout. Error: {success}.', 'danger')

    return redirect(url_for('cart.cart'))

@bp.route('/cart/apply_coupon', methods=['POST'])
@login_required
def apply_coupon():
    coupon_id = request.form.get('coupon_code')

    print(coupon_id)

    if not coupon_id:
        return redirect(url_for('cart.cart'))

    message = Coupon.apply_coupon(current_user.id, coupon_id)
    flash(message, 'success' if 'successfully' in message else 'danger')

    return redirect(url_for('cart.cart'))

@bp.route('/cart/remove_coupon', methods=['POST'])
@login_required
def remove_coupon():
    coupon_id = request.form.get('coupon_id')

    if not coupon_id:
        return redirect(url_for('cart.cart'))

    success = Coupon.remove_coupon(current_user.id, coupon_id)
    if success:
        flash('Coupon removed successfully.', 'success')
    else:
        flash('Failed to remove coupon. Please try again.', 'danger')

    return redirect(url_for('cart.cart'))