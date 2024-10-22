from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, user_id, email, full_name, address):
        self.id = user_id
        self.email = email
        self.full_name = full_name
        self.address = address

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password_hash, user_id, email, full_name, address
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
SELECT user_id, email, full_name, address
FROM Users
WHERE user_id = :user_id
""",
                              user_id=user_id)
        return User(*(rows[0])) if rows else None

    def is_seller(user_id):
        rows = app.db.execute('''
            SELECT *
            FROM Users
            WHERE user_id = :user_id AND is_seller = TRUE
        ''', user_id=user_id)
        return len(rows) == 1