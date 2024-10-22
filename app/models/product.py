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