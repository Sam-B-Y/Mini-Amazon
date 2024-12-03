from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from .models.product import Product, Category

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

@bp.route('/products', methods=['GET'])
def get_products():
    keywords = request.args.get('q')
    category = request.args.get('category')
    sort = request.args.get('sort')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('limit', default=10, type=int)
    
    products = Product.search(keywords=keywords, category=category, sort_by_price=sort)
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'products': [p.to_dict() for p in products[start:end]],
        'total_products': len(products),
        'page': page,
        'pages': (len(products) + per_page - 1) // per_page
    })

@bp.route('/products/<int:product_id>')
def get_product(product_id):
    product = Product.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product.to_dict())

@bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product = Product.create(
        category_name=data['category_name'],
        name=data['name'],
        description=data['description'],
        image_url=data['image_url'],
        price=float(data['price']),
        created_by=data['created_by']
    )
    if product:
        return jsonify(product.to_dict()), 201
    return jsonify({'error': 'Failed to create product'}), 400

@bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = Product.update(
        product_id=product_id,
        category_name=data['category_name'],
        name=data['name'],
        description=data['description'],
        image_url=data['image_url'],
        price=float(data['price'])
    )
    if product:
        return jsonify(product.to_dict())
    return jsonify({'error': 'Failed to update product'}), 400

@bp.route('/products/create', methods=['GET'])
def create_product_form():
    categories = Category.get_all()
    return render_template('product_create.html', categories=categories)

@bp.route('/products/<int:product_id>/edit', methods=['GET'])
def edit_product_form(product_id):
    product = Product.get(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('products.get_products'))
    
    categories = Category.get_all()
    return render_template('product_edit.html', 
                         product=product,
                         categories=categories)
