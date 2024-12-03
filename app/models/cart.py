from flask import current_app as app

class Cart:
    def __init__(self, cart_item_id, user_id, product_id, seller_id, quantity, added_at, image_url, name, price, created_by):
        self.cart_item_id = cart_item_id
        self.user_id = user_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.quantity = quantity
        self.added_at = added_at
        self.image_url = image_url
        self.name = name
        self.price = price
        self.created_by = created_by

    @staticmethod
    def get_by_user(user_id):
        """
        Retrieve all items in the cart for a given user.
        """
        rows = app.db.execute("""
        SELECT 
            c.cart_item_id, 
            c.user_id, 
            c.product_id, 
            c.seller_id, 
            c.quantity, 
            c.added_at, 
            p.image_url, 
            p.name, 
            p.price,
            p.created_by
        FROM CartItems c
        JOIN Products p ON c.product_id = p.product_id
        WHERE c.user_id = :user_id
        ORDER BY c.added_at ASC
        """, user_id=user_id)
        # If no items found, return an empty list
        if not rows:
            return []

        # Return a list of Cart objects
        return [Cart(*row) for row in rows]

    @staticmethod
    def add_item(user_id, product_id, seller_id, quantity):
        """
        Add a new item to the cart for the user.
        If the item already exists, add to its quantity.
        """
        try:
            row = app.db.execute("""
                SELECT quantity FROM CartItems 
                WHERE user_id = :user_id AND product_id = :product_id
            """, user_id=user_id, product_id=product_id)
            if row:
                new_quantity = row.quantity + quantity
                app.db.execute("""
                    UPDATE CartItems
                    SET quantity = :quantity
                    WHERE user_id = :user_id AND product_id = :product_id
                """, quantity=new_quantity, user_id=user_id, product_id=product_id)
            else:
                app.db.execute("""
                    INSERT INTO CartItems(user_id, product_id, seller_id, quantity)
                    VALUES (:user_id, :product_id, :seller_id, :quantity)
                """, user_id=user_id, product_id=product_id, seller_id=seller_id, quantity=quantity)
            return True
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            return False

    @staticmethod
    def update_item_quantity(cart_item_id, quantity):
        """
        Update the quantity of a cart item.
        """
        try:
            # Check if the cart item exists
            row = app.db.execute("""
            SELECT user_id FROM CartItems WHERE cart_item_id = :cart_item_id
            """, cart_item_id=cart_item_id)
            if not row:
                print(f"Cart item {cart_item_id} does not exist.")
                return False

            app.db.execute("""
            UPDATE CartItems
            SET quantity = :quantity
            WHERE cart_item_id = :cart_item_id
            """, cart_item_id=cart_item_id, quantity=quantity)
            return True
        except Exception as e:
            print(f"Error updating item quantity: {e}")
            return False

    @staticmethod
    def remove_item(cart_item_id):
        """
        Remove an item from the cart.
        """
        try:
            # Check if the cart item exists
            row = app.db.execute("""
            SELECT user_id FROM CartItems WHERE cart_item_id = :cart_item_id
            """, cart_item_id=cart_item_id)
            if not row:
                print(f"Cart item {cart_item_id} does not exist.")
                return False

            app.db.execute("""
            DELETE FROM CartItems
            WHERE cart_item_id = :cart_item_id
            """, cart_item_id=cart_item_id)
            return True
        except Exception as e:
            print(f"Error removing item from cart: {e}")
            return False
