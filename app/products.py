from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from .models.product import Product, Category
from .models.inventory import Inventory


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

@bp.route('/products/search_existing', methods=['GET'])
def search_existing_product():
    keywords = request.args.get('q', '').strip()  # Get the search query
    if not keywords:
        return jsonify({'error': 'No keywords provided.'}), 400

    # Use the new search_and_return_existing method
    products = Product.search_and_return_existing(keywords)
    if not products:
        return jsonify({'products': [], 'message': 'No matching products found.'})
    
    return jsonify({'products': products})


@bp.route('/products/create_listing', methods=['POST'])
def create_listing():
    """
    Create a listing for an existing product.
    """
    user_id = request.cookies.get('id')    # Automatically fetch user_id from session

    # Validate that the user is logged in
    if not user_id:
        return jsonify({'error': 'User not authenticated. Please log in.'}), 401

    data = request.get_json()

    product_id = data.get('product_id')
    quantity = data.get('quantity')

    # Validate required fields
    if not product_id or not quantity:
        return jsonify({'error': 'Product ID and quantity are required.'}), 400

    # Use the Inventory model to create a listing
    success = Inventory.create_listing(user_id, product_id, quantity)

    if success:
        return jsonify({'message': 'Listing created successfully!'}), 201
    else:
        return jsonify({'error': 'Failed to create listing.'}), 500



@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    reviews = Product.get_reviews(product_id)
    inventory = Inventory.get_stock(product_id)
    return render_template('/products/product_detail.html', product=product, reviews=reviews, inventory=inventory)

@bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    user_id = request.cookies.get('id')
    product = Inventory.add(
        category_name=data['category_name'],
        name=data['name'],
        description=data['description'],
        image_url=data['image_url'],
        price=float(data['price']),
        user_id=user_id,
        quantity=data['quantity']
    )
    if product[0]:
        product_id = product[1]
        product_obj = Product.get(product_id)
        print(product_obj)
        return jsonify(product_obj.to_dict()), 201
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
    return render_template('/products/product_edit.html', 
                         product=product,
                         categories=categories)
