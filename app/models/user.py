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
    def get_product_history(user_id):
        rows = app.db.execute('''
SELECT name, description, category_name, ordered_time, image_url, quantity, price
FROM OrderItems
JOIN Orders ON Orders.order_id = OrderItems.order_id
JOIN Products ON Products.product_id=OrderItems.product_id                              
WHERE user_id = :user_id
''',
                              user_id=user_id)
        return rows
