from flask import Blueprint, request, jsonify, render_template
from .models.user import User
from .models.inventory import Inventory

bp = Blueprint('inventory', __name__)

@bp.route('/api/inventory', methods=['GET'])
def search():
    user_id = request.args.get('user_id')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('limit', default=10, type=int)  # Items per page, default to 10

    if not User.is_seller(user_id):
        return jsonify({"error": "User is not a seller"}), 401

    # Get the seller's inventory
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

@bp.route('/inventory', methods=['GET'])
def inventory_page():
    return render_template('inventory.html')
