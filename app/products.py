from flask import Blueprint, request, jsonify, render_template
from .models.product import Product

bp = Blueprint('products', __name__)

@bp.route('/top_expensive', methods=['GET'])
def get_top_expensive_products():
    k = request.args.get('k', default=1000, type=int) 
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('limit', default=10, type=int)
    
    products = Product.get_top_expensive(k)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_products = products[start:end]
    
    return jsonify({
        'products': [p.to_dict() for p in paginated_products],
        'total_products': len(products),
        'page': page,
        'pages': (len(products) + per_page - 1) // per_page
    })

@bp.route('/top_expensive_page')
def top_expensive_page():
    return render_template('top_expensive_products.html')
