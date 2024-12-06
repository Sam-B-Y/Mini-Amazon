from flask import current_app as app
from datetime import datetime

class Coupon:
    def __init__(self, coupon_id, name, categories, discount, expiry_date):
        self.coupon_id = coupon_id
        self.name = name
        self.categories = categories
        self.discount = discount
        self.expiry_date = expiry_date

    @staticmethod
    def get_all_coupons():
        rows = app.db.execute("""
        SELECT coupon_id, name, categories, discount, expiry_date
        FROM Coupons
        WHERE expiry_date >= NOW()
        """)
        return [Coupon(*row) for row in rows]
    
    @staticmethod
    def get_cart_coupons(user_id):
        rows = app.db.execute("""
        SELECT c.coupon_id, c.name, c.categories, c.discount, c.expiry_date
        FROM AppliedCoupons ac
        JOIN Coupons c ON ac.coupon_id = c.coupon_id
        WHERE ac.user_id = :user_id AND ac.cart = TRUE
        """, user_id=user_id)
        return [Coupon(*row) for row in rows]
    
    @staticmethod
    def get_user_available_coupons(user_id):
        rows = app.db.execute("""
        SELECT c.coupon_id, c.name, c.categories, c.discount, c.expiry_date
        FROM Coupons c
        WHERE c.expiry_date >= NOW()
        AND NOT EXISTS (
            SELECT 1 FROM AppliedCoupons ac
            WHERE ac.user_id = :user_id AND ac.coupon_id = c.coupon_id
        )
        """, user_id=user_id)
        return [Coupon(*row) for row in rows]

    @staticmethod
    def get_coupon_by_id(coupon_id):
        row = app.db.execute("""
        SELECT coupon_id, name, categories, discount, expiry_date
        FROM Coupons
        WHERE coupon_id = :coupon_id
        """, coupon_id=coupon_id)
        return Coupon(*row[0]) if row else None

    @staticmethod
    def apply_coupon(user_id, coupon_id, order_id=None):
        try:
            coupon = Coupon.get_coupon_by_id(coupon_id)
            if not coupon:
                return "Coupon not found."
            if coupon.expiry_date < datetime.now().date():
                return "Coupon has expired."
            row = app.db.execute("""
            SELECT 1 FROM AppliedCoupons
            WHERE user_id = :user_id AND coupon_id = :coupon_id
            """, user_id=user_id, coupon_id=coupon_id)
            if row:
                return "Coupon already applied."
            app.db.execute("""
            INSERT INTO AppliedCoupons(user_id, coupon_id, cart, order_id)
            VALUES(:user_id, :coupon_id, :cart, :order_id)
            """, user_id=user_id, coupon_id=coupon_id, cart=True if order_id is None else False, order_id=order_id or 0)
            return "Coupon applied successfully."
        except Exception as e:
            print(f"Error applying coupon: {e}")
            return "Error applying coupon."

    @staticmethod
    def remove_coupon(user_id, coupon_id):
        try:
            app.db.execute("""
            DELETE FROM AppliedCoupons
            WHERE user_id = :user_id AND coupon_id = :coupon_id
            """, user_id=user_id, coupon_id=coupon_id)
            return True
        except Exception as e:
            print(f"Error removing coupon: {e}")
            return False

    @staticmethod
    def get_applied_coupons(user_id):
        rows = app.db.execute("""
        SELECT c.coupon_id, c.name, c.categories, c.discount, c.expiry_date
        FROM AppliedCoupons ac
        JOIN Coupons c ON ac.coupon_id = c.coupon_id
        WHERE ac.user_id = :user_id
        """, user_id=user_id)
        return [Coupon(*row) for row in rows]
    
    @staticmethod
    def get_order_coupons(order_id):
        rows = app.db.execute("""
        SELECT c.coupon_id, c.name, c.categories, c.discount, c.expiry_date
        FROM AppliedCoupons ac
        JOIN Coupons c ON ac.coupon_id = c.coupon_id
        WHERE ac.order_id = :order_id
        """, order_id=order_id)
        return [Coupon(*row) for row in rows]
