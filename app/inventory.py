from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask import current_app as app

from .models.user import User
from .models.inventory import Inventory

bp = Blueprint('inventory', __name__)

@bp.route('/api/inventory', methods=['GET'])
def search():
    user_id = request.args.get('user_id')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('limit', default=10, type=int)  # Items per page, default to 10

    # Remove the seller check
    # if not User.is_seller(user_id):
    #     return jsonify({"error": "User is not a seller"}), 401

    # Get the inventory for the user (without checking if they're a seller)
    inventory = Inventory.get(user_id)

    # Calculate paginated inventory
    start = (page - 1) * per_page
    end = start + per_page
    paginated_inventory = inventory[start:end]

    inventory_list = [
        {
            'inventory_id': item['inventory_id'],
            'seller_id': item['seller_id'],
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'product_name': item['product_name'],
            'description': item['description'],
            'image_url': item['image_url'],
            'price': item['price']
        } for item in paginated_inventory
    ]

    return jsonify({
        'inventory': inventory_list,
        'total_items': len(inventory),
        'page': page,
        'pages': (len(inventory) + per_page - 1) // per_page  # Total number of pages
    })


@bp.route('/add_inventory', methods=['POST'])
def add_inventory():
    try:
        user_id = request.cookies.get('id')  # Assuming the user ID is stored in cookies
        if not user_id:
            return jsonify({"error": "User ID not found. Please log in."}), 400

        # Get JSON data
        data = request.get_json()

        # Extract fields from JSON
        category_name = data.get('category_name')
        name = data.get('name')
        description = data.get('description')
        image_url = data.get('image_url')
        price = data.get('price')
        quantity = data.get('quantity')

        # Validate required fields
        if not category_name or not name or not description or not image_url or price is None or quantity is None:
            return jsonify({"error": "All fields are required."}), 400

        # Check if the category exists, create it if it doesn't
        if not Inventory.category_exists(category_name):
            Inventory.add_category(category_name)

        # Add the product and inventory
        result = Inventory.add(user_id, category_name, name, description, image_url, price, quantity)
        if result:
            return jsonify({"success": "Item added successfully!"}), 200
        else:
            return jsonify({"error": "Failed to add item to inventory."}), 500

    except Exception as e:
        print(f"Error adding to inventory: {e}")
        return jsonify({"error": "An error occurred while adding the item."}), 500

    
@bp.route('/api/delete_product', methods=['DELETE'])
def delete_product():
    try:
        data = request.get_json()
        inventory_id = data.get('inventory_id')

        if inventory_id is None:
            return jsonify({"error": "Invalid input"}), 400

        app.db.execute('''
            DELETE FROM Inventory
            WHERE inventory_id = :inventory_id
        ''', inventory_id=inventory_id)

        return jsonify({"success": "Product deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/api/update_quantity', methods=['POST'])
def update_quantity():
    try:
        data = request.get_json()
        inventory_id = data.get('inventory_id')
        quantity = data.get('quantity')

        if inventory_id is None or quantity is None:
            return jsonify({"error": "Invalid input"}), 400

        app.db.execute('''
            UPDATE Inventory
            SET quantity = :quantity
            WHERE inventory_id = :inventory_id
        ''', quantity=quantity, inventory_id=inventory_id)

        return jsonify({"success": "Quantity updated successfully"}), 200
    except Exception as e:
        print(f"Error updating quantity: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/inventory', methods=['GET'])
def inventory_page():
    return render_template('inventory.html')
