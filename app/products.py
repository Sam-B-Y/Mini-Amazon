from flask import Blueprint, request, jsonify, render_template
from .models.product import Product

bp = Blueprint('products', __name__)

@bp.route('/top_expensive', methods=['GET'])
def get_top_expensive_products():
    k = request.args.get('k', default=10, type=int)
    products = Product.get_top_expensive(k)
    return jsonify([p.to_dict() for p in products])

@bp.route('/top_expensive_page')
def top_expensive_page():
    return render_template('top_expensive_products.html')