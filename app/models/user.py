from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, user_id, email, full_name, address, balance):
        self.id = user_id
        self.email = email
        self.full_name = full_name
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password_hash, user_id, email, full_name, address, balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, full_name, address):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password_hash, full_name, address)
VALUES(:email, :password_hash, :full_name, :address)
RETURNING user_id
""",
                                  email=email,
                                  password_hash=generate_password_hash(password),
                                  full_name=full_name, address=address)
            user_id = rows[0][0]
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(user_id):
        rows = app.db.execute("""
SELECT user_id, email, full_name, address, balance
FROM Users
WHERE user_id = :user_id
""",
                              user_id=user_id)
        return User(*(rows[0])) if rows else None

    def get_email_from_id(user_id):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE user_id = :user_id
""",
                              user_id=user_id)
        return rows[0][0] if rows else None

    @staticmethod
    def update(user_id, field, new_value):
        if field == "balance":
            try:
                float(new_value)
            except ValueError:
                return None

        if field in ["full_name", "address", "balance"]:
            app.db.execute(f"""
    UPDATE users SET {field} = :new_value WHERE user_id=:user_id
    """, field=field, new_value=new_value, user_id=user_id)
        
        return None
    
    @staticmethod
    def get_product_history(user_id, page=1, per_page=10):
        offset = (page - 1) * per_page

        # get name, description, category_name, ordered_time, image_url, quantity, price, seller_id, product_id then group by order_id
        rows = app.db.execute('''
            SELECT 
                o.order_id, o.ordered_time, o.status, 
                i.product_id, i.seller_id, i.quantity, p.price, p.name, p.description, p.image_url, p.category_name
            FROM Orders o
            JOIN OrderItems i ON o.order_id = i.order_id
            JOIN Products p ON i.product_id = p.product_id
            WHERE o.user_id = :user_id
            ORDER BY o.ordered_time DESC
            LIMIT :per_page OFFSET :offset
        ''', user_id=user_id, per_page=per_page, offset=offset)

        total_items = app.db.execute('''
            SELECT COUNT(DISTINCT o.order_id)
            FROM Orders o
            JOIN OrderItems i ON o.order_id = i.order_id
            JOIN Products p ON i.product_id = p.product_id
            WHERE o.user_id = :user_id
        ''', user_id=user_id)[0][0]


        return {
            "rows": rows,
            "total_items": total_items,
            "page": page,
            "pages": (total_items + per_page - 1) // per_page
        }


    def is_seller(user_id):
        rows = app.db.execute('''
            SELECT *
            FROM Users
            WHERE user_id = :user_id AND is_seller = TRUE
        ''', user_id=user_id)
        return len(rows) == 1

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT user_id, email, full_name, address, balance
FROM Users
''')
        return [User(*row) for row in rows]
    

    @staticmethod
    def get_seller_stats(user_id):
        rows = app.db.execute('''
            SELECT 
                SUM(p.price * oi.quantity) AS total_sales, 
                COUNT(DISTINCT o.order_id) AS total_orders,
                AVG(r.rating) AS average_rating,
                COUNT(DISTINCT i.product_id) AS products_listed
            FROM OrderItems oi
            JOIN inventory i ON i.product_id = oi.product_id
            JOIN Products p ON p.product_id = oi.product_id
            JOIN Orders o ON o.order_id = oi.order_id
            LEFT JOIN Reviews r ON r.product_id = i.product_id
            WHERE i.seller_id = :user_id
        ''', user_id=user_id)
        return rows[0] if None not in rows[0] else None
    
    @staticmethod
    def save(self):
        app.db.execute('''
    UPDATE Users
    SET email = :email, full_name = :full_name, address = :address, balance = :balance
    WHERE user_id = :user_id
    ''', user_id=self.id, email=self.email, full_name=self.full_name, address=self.address, balance=self.balance)
        
    def become_seller(user_id):
        app.db.execute('''
            UPDATE Users
            SET is_seller = TRUE
            WHERE user_id = :user_id
        ''', user_id=user_id)
    