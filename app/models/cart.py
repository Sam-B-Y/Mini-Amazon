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
        
    @staticmethod
    def checkout(user_id):
        """
        Process the checkout for a user, updating balances and inventory.
        """
        try:


            user_row = app.db.execute("""
                SELECT balance
                FROM users
                WHERE user_id = :user_id
            """, user_id=user_id)

            if not user_row:
                print("User not found.")
                return "User not found."

            cart_items = app.db.execute("""
                SELECT cart_item_id, product_id, seller_id, quantity
                FROM CartItems
                WHERE user_id = :user_id
            """, user_id=user_id)

            if not cart_items:
                print("Cart is empty.")
                return "Empty cart."


            user_balance = user_row[0][0]
            total_cost = 0
            items_to_purchase = []
            seller_totals = {}

            for item in cart_items:
                cart_item_id, product_id, seller_id, quantity = item
                inventory_row = app.db.execute("""
                    SELECT quantity
                    FROM inventory
                    WHERE seller_id = :seller_id AND product_id = :product_id
                """, seller_id=seller_id, product_id=product_id)

                if not inventory_row:
                    print(f"Product {product_id} not found in inventory of seller {seller_id}.")
                    product_name = app.db.execute("""
                        SELECT name
                        FROM products
                        WHERE product_id = :product_id
                    """, product_id=product_id)[0][0]

                    print(f"Product name: {product_name}")
                    return f"Product {product_name} not found in inventory."

                inventory_quantity = inventory_row[0][0]
                if inventory_quantity < quantity:
                    product_name = app.db.execute("""
                        SELECT name
                        FROM products
                        WHERE product_id = :product_id
                    """, product_id=product_id)[0][0]

                    print(f"Insufficient quantity of {product_name} in inventory.")
                    
                    return f"Insufficient quantity of {product_name} in inventory."

                price_row = app.db.execute("""
                    SELECT price
                    FROM products
                    WHERE product_id = :product_id
                """, product_id=product_id)

                unit_price = price_row[0][0]
                total_cost += unit_price * quantity
                items_to_purchase.append((product_id, seller_id, quantity, unit_price))

                seller_totals[seller_id] = seller_totals.get(seller_id, 0) + unit_price * quantity

            total_after_coupons = total_cost

            user_coupons = app.db.execute("""
                SELECT coupon_id, discount
                FROM AppliedCoupons
                WHERE user_id = :user_id AND cart = TRUE
            """, user_id=user_id)

            for coupon_id, discount in user_coupons:
                total_after_coupons -= total_after_coupons * discount / 100

            total_after_coupons = round(total_after_coupons, 2)

            if user_balance < total_after_coupons:
                print("User does not have enough balance.")
                return "Insufficient balance."

            app.db.execute("""
                UPDATE users
                SET balance = balance - :total_after_coupons
                WHERE user_id = :user_id
            """, total_after_coupons=total_after_coupons, user_id=user_id)

            for seller_id, amount in seller_totals.items():
                app.db.execute("""
                    UPDATE users
                    SET balance = balance + :amount
                    WHERE user_id = :seller_id
                """, amount=amount, seller_id=seller_id)

            for product_id, seller_id, quantity, _ in items_to_purchase:
                app.db.execute("""
                    UPDATE inventory
                    SET quantity = quantity - :quantity
                    WHERE seller_id = :seller_id AND product_id = :product_id
                """, quantity=quantity, seller_id=seller_id, product_id=product_id)

            order_id_rows = app.db.execute("""
                INSERT INTO orders(user_id, status, ordered_time)
                VALUES(:user_id, 'Ordered', NOW())
                RETURNING order_id
            """, user_id=user_id)
            order_id = order_id_rows[0][0]

            for product_id, seller_id, quantity, unit_price in items_to_purchase:
                app.db.execute("""
                    INSERT INTO OrderItems(order_id, product_id, seller_id, quantity, unit_price)
                    VALUES(:order_id, :product_id, :seller_id, :quantity, :unit_price)
                """, order_id=order_id, product_id=product_id, seller_id=seller_id, quantity=quantity, unit_price=unit_price)

            app.db.execute("""
                DELETE FROM cartitems
                WHERE user_id = :user_id
            """, user_id=user_id)

            return "success"
        except Exception as e:
            print(f"Error during checkout: {e}")
            return "Error during checkout."
