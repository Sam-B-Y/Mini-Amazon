from flask import Blueprint, request, jsonify
from .models.user import User
from .models.inventory import Inventory

bp = Blueprint('inventory', __name__)

@bp.route('/inventory', methods=['GET'])
def search():
    user_id = request.args.get('user_id')
    
    # Check if the user is a seller
    if not User.is_seller(user_id):
        return jsonify({"error": "User is not a seller"}), 401
    
    # Get inventory data along with product details
    inventory = Inventory.get(user_id)
    
    # Convert each row into a dictionary that includes both inventory and product details
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
        } for item in inventory
    ]
    
    # Return the list of inventory and product details as JSON
    return jsonify(inventory_list)
