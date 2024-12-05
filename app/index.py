from flask import render_template
from flask_login import current_user

from .models.product import Product

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    # Fetch top-selling products (Hot Products)
    hot_products = Product.get_top_selling_products(limit=10)

    print(hot_products)

    # Fetch Christmas products
    christmas_products = Product.search_by_keyword('christmas')

    return render_template('index.html',
                           hot_products=hot_products,
                           christmas_products=christmas_products)
