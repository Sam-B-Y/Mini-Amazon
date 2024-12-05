from flask import current_app as app
from flask import session
import re
import logging

class Product:
    def __init__(self, product_id, category_name, name, description, image_url, price, created_by):
        self.product_id = product_id
        self.category_name = category_name
        self.name = name
        self.description = description
        self.image_url = image_url
        self.price = price
        self.created_by = created_by

    @staticmethod
    def get(product_id):
        rows = app.db.execute('''
SELECT product_id, category_name, name, description, image_url, price, created_by
FROM Products
WHERE product_id = :product_id
''', 
                              product_id=product_id)
        return Product(*(rows[0])) if rows is not None and rows else None

    @staticmethod
    def get_reviews(product_id):
        rows = app.db.execute('''
SELECT r.review_id, r.rating, r.comment, r.added_at, u.full_name AS reviewer_name
FROM Reviews r
JOIN Users u ON r.user_id = u.user_id
WHERE r.product_id = :product_id
''', 
                              product_id=product_id)
        return [{'review_id': r[0], 'rating': r[1], 'comment': r[2], 'added_at': r[3], 'reviewer_name': r[4]} for r in rows]

    @staticmethod
    def get_sellers(product_id):
        rows = app.db.execute('''
SELECT u.user_id AS seller_id, u.full_name AS seller_name, i.quantity
FROM Users u
JOIN Inventory i ON u.user_id = i.seller_id
WHERE i.product_id = :product_id AND u.is_seller = TRUE
''', 
                              product_id=product_id)
        return [{'seller_id': r[0], 'seller_name': r[1], 'quantity': r[2]} for r in rows]

    @staticmethod
    def search(keywords=None, category=None, sort_by_price=None):
        query = "SELECT * FROM Products WHERE 1=1"
        params = {}

        if keywords:
            query += " AND name LIKE :keywords"
            params['keywords'] = f"%{keywords}%"
        
        if category:
            query += " AND category_name = :category"
            params['category'] = category
        
        if sort_by_price:
            query += " ORDER BY price " + ("ASC" if sort_by_price == "asc" else "DESC")

        rows = app.db.execute(query, **params)
        return [Product(*row) for row in rows]

    def to_dict_search(self):
        return {
            'product_id': self.product_id,
            'category_name': self.category_name,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'price': float(self.price),
            'created_by': self.created_by
        }

    @staticmethod
    def search_and_return_existing(keywords):
        """Search for products based on keywords and return their details."""
        products = Product.search(keywords=keywords)
        return [p.to_dict_search() for p in products]  # Convert Product objects to dictionaries

    

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT product_id, category_name, name, description, image_url, price, created_by
FROM Products
''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get_top_expensive(k):
        rows = app.db.execute('''
            SELECT *
            FROM Products
            ORDER BY price DESC
            LIMIT :k
        ''', k=k)
        return [Product(*row) for row in rows]

    @staticmethod
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'category_name': self.category_name,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'price': self.price,
            'created_by': self.created_by
        }
    
    @staticmethod
    def search_by_keyword(keywords):
        words = keywords.split()
        params = {}
        relevance_exprs = []
        where_clauses = []

        for idx, word in enumerate(words):
            param = f'word{idx}'
            word_pattern = f'%{word.lower()}%'
            params[param] = word_pattern

            relevance_exprs.append(f"""
                (CASE WHEN LOWER(p.name) LIKE :{param} THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(p.category_name) LIKE :{param} THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(p.description) LIKE :{param} THEN 1 ELSE 0 END)
            """)
            
            where_clauses.append(f"""
                LOWER(p.name) LIKE :{param} OR
                LOWER(p.category_name) LIKE :{param} OR
                LOWER(p.description) LIKE :{param}
            """)

        relevance_expr = ' + '.join(relevance_exprs)
        where_clause = ' OR '.join(where_clauses)

        query = f'''
        SELECT p.product_id, p.category_name, p.name, p.description, p.image_url, p.price, p.created_by,
        ({relevance_expr}) AS relevance,
        COALESCE(AVG(r.rating), 0) AS avg_review_score,
        COUNT(r.review_id) AS review_count
        FROM Products p
        LEFT JOIN Reviews r ON p.product_id = r.product_id
        WHERE {where_clause}
        GROUP BY p.product_id, p.category_name, p.name, p.description, p.image_url, p.price, p.created_by
        ORDER BY relevance DESC, p.product_id
        '''
        rows = app.db.execute(query, **params)
        return [{
            'product_id': row[0],
            'category_name': row[1],
            'name': row[2],
            'description': row[3],
            'image_url': row[4],
            'price': row[5],
            'created_by': row[6],
            'relevance': row[7],
            'avg_review_score': row[8],
            'review_count': row[9]
        } for row in rows]
    
    @staticmethod
    def best_search_by_keyword(keywords):
        results = Product.search_by_keyword(keywords)

        if not results:
            return False

        return sorted(results, key=lambda x: x['relevance'], reverse=True)[0]

    @staticmethod
    def handle_follow_up(message, product):
        message = message.lower()
        if 'price' in message:
            return f"The price of **{product.name}** is **${product.price}**.", False
        elif 'description' in message:
            return f"**Description:** {product.description}", False
        elif 'image' in message:
            return f"**Image URL:** {product.image_url}", False
        elif 'buy' in message or 'purchase' in message:
            return f"You can purchase **{product.name}** for **${product.price}** [here]({product.image_url}).", False
        elif 'other' in message or 'different' in message:
            return "Sure, what else are you looking for?", True
        else:
            return "I can help you with the price, description, or image of the product. How can I assist you further?", False

    @staticmethod
    def format_product_response(product):
        response = (
            f"**{product['name']}**\n"
            f"Category: {product['category_name']}\n"
            f"Description: {product['description']}\n"
            f"Price: ${product['price']}\n"
            f"Image: {product['image_url']}\n"
            f"How can I assist you further with this product?"
        )
        return response
    
    @staticmethod 
    def get_all_info_by_id(product_id):
        product = Product.get(product_id)
        product = Product.to_dict(product)
        del product['created_by']
        if not product:
            return None
        reviews = Product.get_reviews(product_id)
        sellers = Product.get_sellers(product_id)
        inventory = sum(seller['quantity'] for seller in sellers)
        return {
            'product': product,
            'reviews': reviews,
            'inventory': inventory,
            'sellers': sellers
        }

class Category:
    def __init__(self, category_name):
        self.category_name = category_name

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT category_name
FROM Categories
''')
        return [Category(row[0]) for row in rows]
