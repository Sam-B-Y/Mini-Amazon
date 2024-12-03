from flask import current_app as app

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
SELECT s.seller_id, s.seller_name, s.quantity
FROM Sellers s
JOIN Inventory i ON s.seller_id = i.seller_id
WHERE i.product_id = :product_id
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
