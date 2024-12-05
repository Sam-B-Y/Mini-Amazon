from flask import Blueprint, request, jsonify
from flask import render_template
from .models.product import Product

bp = Blueprint('search', __name__)

#TODO implement this, probably require 3 characters to start searching, then match based on *query* (case insensitive) in product name, description, and category

@bp.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')

    if not query:
        query = request.args.get('query2')

    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    results = perform_search(query.lower())

    range_min = float('inf')
    range_max = 0

    for r in results:
        if r['price'] < range_min:
            range_min = r['price']
        if r['price'] > range_max:
            range_max = r['price']

    min_review = request.args.get('min_review', 0, type=float)
    price_min = request.args.get('price_min', 0, type=float)
    price_max = request.args.get('price_max', float('inf'), type=float)
    category = request.args.get('category', '')

    categories = []
    for r in results:
        if r['category_name'] not in categories:
            categories.append(r['category_name'])

    products = results

    if min_review or price_min or price_max < float('inf') or category:
        products = []
        for r in results:
            if r['price'] >= price_min and r['price'] <= price_max and r['avg_review_score'] >= min_review and (not category or r['category_name'] == category ):
                products.append(r)


    sort_setting = request.args.get('sort_by', 'relevance')
    asc = request.args.get('sort_order', 'desc') == 'asc'

    if sort_setting == 'relevance':
        products = sorted(products, key=lambda x: x['relevance'], reverse=not asc)

    elif sort_setting == 'price':
        products = sorted(products, key=lambda x: x['price'], reverse=not asc)

    elif sort_setting == 'rating':
        # for ties, sort by review count
        products = sorted(products, key=lambda x: (x['avg_review_score'], x['review_count']), reverse=not asc)

    else:
        products = sorted(products, key=lambda x: x['review_count'], reverse=not asc)       


    return render_template('search.html',
                           products=products,
                           query=query,
                           min_review=min_review,
                           price_min=price_min,
                           price_max=price_max,
                           category=category,
                           categories=categories,
                           range_min=range_min,
                           range_max=range_max,
                           sort_by=sort_setting,
                           sort_order='asc' if asc else 'desc')


def perform_search(query):
    print(f"Searching for {query}")
    relevant_items = Product.search_by_keyword(query)

    return relevant_items