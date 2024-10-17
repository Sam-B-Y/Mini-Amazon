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