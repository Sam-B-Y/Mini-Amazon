from flask import jsonify, request, render_template
from flask_login import current_user
from .models.review import Review

from flask import Blueprint
bp = Blueprint('reviews', __name__)

@bp.route('/api/reviews/product', methods=['GET'])
def product_reviews():
    product_id, seller_id = request.args.get('product'), request.args.get('seller')
    print(request.args)
    reviews = Review.get_product_reviews(product_id, seller_id)
    return jsonify([{'id': r.review_id, 'product_id': r.product_id, 'seller': r.seller_id, 'rating:': r.rating,'comment:':r.comment,'timestamp': r.added_at} for r in reviews])

@bp.route('/api/reviews/recent', methods=['GET'])
def recent_reviews():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login first'}), 401
    reviews = Review.get_recent(current_user.id)
    return jsonify([{'id': r.review_id, 'product_id': r.product_id, 'seller': r.seller_id, 'rating:': r.rating,'comment:':r.comment,'timestamp': r.added_at} for r in reviews])

@bp.route('/reviewsproduct', methods = ['GET'])
def reviews_product():
    return render_template('reviewsproduct.html')

@bp.route('/reviewsrecent', methods = ['GET'])
def reviews_page():
    return render_template('reviewsrecent.html')
