from flask import Blueprint, request, jsonify
from flask_login import current_user
from .models.purchase import Purchase

bp = Blueprint('orders', __name__)

@bp.route('/api/seller_orders', methods=['GET'])
def seller_orders():
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "User not logged in."}), 401

        seller_id = current_user.id
        search_query = request.args.get('search', "")
        status_filter = request.args.get('status', "")


        if status_filter == "All":
            orders = Purchase.get_orders_by_seller(seller_id, search_query)
        else:
            orders = Purchase.get_orders_by_seller(seller_id, search_query, status_filter)

        return jsonify({"orders": orders}), 200

    except Exception as e:
        print(f"Error fetching seller orders: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
