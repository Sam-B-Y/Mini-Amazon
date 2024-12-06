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

        # Get current status of the line item
        current_status = Purchase.get_line_item_status(order_id, product_id, seller_id)

        if current_status == "Ordered":
            new_status = "Pending"
        elif current_status == "Pending":
            new_status = "Complete"
        else:
            return jsonify({"message": "Line item is already marked as Complete."}), 200

        # Update the status of the line item
        success = Purchase.update_line_item_status(order_id, product_id, seller_id, new_status)

        if not success:
            return jsonify({"error": "Failed to update item status."}), 400

        # Check if the entire order should be marked as complete
        if new_status == "Complete":
            Purchase.update_order_status_if_complete(order_id)

        return jsonify({"success": f"Line item marked as {new_status}."}), 200
    except Exception as e:
        print(f"Error marking item as complete: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
    

@bp.route('/api/update_line_item_status', methods=['POST'])
def update_line_item_status():
    try:
        data = request.get_json()
        order_id = data.get("order_id")
        product_id = data.get("product_id")
        status = data.get("status")

        if not order_id or not product_id or not status:
            return jsonify({"error": "Invalid data provided."}), 400

        success = Purchase.update_line_item_status(order_id, product_id, current_user.id, status)
        if not success:
            return jsonify({"error": "Failed to update line item status."}), 400

        return jsonify({"success": f"Line item status updated to {status}."}), 200
    except Exception as e:
        print(f"Error updating line item status: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500





@bp.route('/api/line_orders', methods=['GET'])
def get_line_orders():
    try:
        order_id = request.args.get('order_id')
        if not order_id:
            return jsonify({"error": "Order ID is required."}), 400

        seller_id = current_user.id
        line_orders = Purchase.get_line_items(order_id, seller_id)

        return jsonify({"line_orders": line_orders}), 200
    except Exception as e:
        print(f"Error fetching line orders: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

