from flask import jsonify, request, render_template
from flask_login import current_user
from .models.review import Review
from .models.product import Product
from .models.user import User  # Assuming there's a User model for seller details

from flask import Blueprint
bp = Blueprint('reviews', __name__)

@bp.route('/api/reviews/product', methods=['GET'])
def product_reviews():
    product_id, seller_id = request.args.get('product'), request.args.get('seller')
    print(request.args)
    reviews = Review.get_product_reviews(product_id, seller_id)
    return jsonify([{
        'id': r.review_id,
        'product_id': r.product_id,
        'seller_id': r.seller_id,
        'rating': r.rating,
        'comment': r.comment,
        'timestamp': r.added_at
    } for r in reviews])

@bp.route('/api/reviews/my_product', methods=['GET'])
def my_product_reviews():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    reviews = Review.get_my_product_reviews(current_user.id)
    for review in reviews:
        product = Product.get(review.product_id)
        seller = User.get(review.seller_id)  # Assuming User model has a method to get seller details
        review.product_name = product.name if product else "Unknown Product"
        review.seller_name = seller.full_name if seller else "Unknown Seller"
    return jsonify([{'id': r.review_id, 'product_id': r.product_id, 'product_name': r.product_name, 'seller_id': r.seller_id, 'seller_name': r.seller_name, 'rating': r.rating,'comment':r.comment,'timestamp': r.added_at} for r in reviews])

@bp.route('/api/reviews/my_seller', methods=['GET'])
def my_seller_reviews():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    reviews = Review.get_my_seller_reviews(current_user.id)
    for review in reviews:
        seller = User.get(review.seller_id)  # Assuming User model has a method to get seller details
        review.seller_name = seller.full_name if seller else "Unknown Seller"
    return jsonify([{'id': r.review_id, 'seller_id': r.seller_id, 'seller_name': r.seller_name, 'rating': r.rating,'comment':r.comment,'timestamp': r.added_at} for r in reviews])

@bp.route('/api/reviews/recent', methods=['GET'])
def recent_reviews():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    reviews = Review.get_recent(current_user.id)
    
    # Fetch product names and seller names for each review
    for review in reviews:
        product = Product.get(review.product_id)
        seller = User.get(review.seller_id)  # Assuming User model has a method to get seller details
        review.product_name = product.name if product else "Unknown Product"
        review.seller_name = seller.full_name if seller else "Unknown Seller"
    return jsonify([{'id': r.review_id, 'product_id': r.product_id, 'product_name': r.product_name, 'seller_id': r.seller_id, 'seller_name': r.seller_name, 'rating': r.rating,'comment':r.comment,'timestamp': r.added_at} for r in reviews])

@bp.route('/api/reviews/submit', methods=['POST'])
def submit_review():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    seller_id = data.get('seller_id')
    rating = data.get('rating')
    comment = data.get('comment')

    try:
        Review.submit_product_review(current_user.id, product_id, seller_id, rating, comment)
        return jsonify({'message': 'Review submitted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/api/reviews/seller_review', methods=['POST'])
def submit_seller_review():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    
    data = request.get_json()
    seller_id = data.get('seller_id')
    rating = data.get('rating')
    comment = data.get('comment')

    try:
        Review.submit_seller_review(current_user.id, seller_id, rating, comment)
        return jsonify({'message': 'Seller review submitted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/api/reviews/edit', methods=['POST'])
def edit_review():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    
    data = request.get_json()
    review_id = data.get('review_id')
    rating = data.get('rating')
    comment = data.get('comment')

    try:
        Review.edit_review(review_id, rating, comment)
        return jsonify({'message': 'Review updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/api/reviews/delete', methods=['DELETE'])
def delete_review():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    
    data = request.get_json()
    review_id = data.get('review_id')

    try:
        Review.remove_review(review_id)
        return jsonify({'message': 'Review deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/reviewsproduct', methods = ['GET'])
def reviews_product():
    return render_template('reviewsproduct.html')

@bp.route('/reviewsrecent', methods = ['GET'])
def reviews_page():
    return render_template('/account/my_reviews_updated.html')

@bp.route('/api/reviews/seller/<int:seller_id>', methods=['GET'])
def seller_reviews(seller_id):
    reviews = Review.get_seller_reviews(seller_id)
    return jsonify([{
        'id': r.review_id,
        'product_id': r.product_id,
        'rating': r.rating,
        'comment': r.comment,
        'timestamp': r.added_at
    } for r in reviews])
