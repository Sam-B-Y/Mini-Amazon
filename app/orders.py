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

        # Ensure orders are sorted by 'order_id'
        orders = sorted(orders, key=lambda x: x['order_id'])

        return jsonify({"orders": orders}), 200

    except Exception as e:
        print(f"Error fetching seller orders: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500



@bp.route('/api/mark_complete', methods=['POST'])
def mark_line_item_complete():
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "User not logged in."}), 401

        seller_id = current_user.id
        data = request.get_json()
        order_id = data.get("order_id")
        product_id = data.get("product_id")

        if not order_id or not product_id:
            return jsonify({"error": "Order ID and Product ID are required."}), 400

        success = Purchase.mark_line_item_complete(order_id, product_id, seller_id)

        if not success:
            return jsonify({"error": "Failed to update item status."}), 400

        return jsonify({"success": "Item marked as complete."}), 200
    except Exception as e:
        print(f"Error marking item as complete: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@bp.route('/api/line_orders', methods=['GET'])
def get_line_orders():
    try:
        order_id = request.args.get('order_id')
        if not order_id:
            return jsonify({"error": "Order ID is required."}), 400

        seller_id = current_user.id
        line_orders = Purchase.get_line_items(order_id, seller_id)
        print(line_orders)

        return jsonify({"line_orders": line_orders}), 200
    except Exception as e:
        print(f"Error fetching line orders: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
