from flask import current_app as app

class Inventory: 
    def __init__(self, inventory_id, seller_id, product_id, quantity):
        self.inventory_id = inventory_id
        self.seller_id = seller_id
        self.product_id = product_id
        self.quantity = quantity

    @staticmethod
    def get(seller_id):
        rows = app.db.execute('''
            SELECT i.inventory_id, i.seller_id, i.product_id, i.quantity,
                p.name AS product_name, p.description, p.image_url, p.price, p.category_name
            FROM Inventory i
            JOIN Products p ON i.product_id = p.product_id
            WHERE i.seller_id = :seller_id;
        ''', seller_id=seller_id)
        
        return [dict(
            inventory_id=row[0],
            seller_id=row[1],
            product_id=row[2],
            quantity=row[3],
            product_name=row[4],
            description=row[5],
            image_url=row[6],
            price=row[7],
            category_name=row[8]
        ) for row in rows] if rows else []

    @staticmethod
    def add(user_id, category_name, name, description, image_url, price, quantity):
        try:
            if not Inventory.category_exists(category_name):
                Inventory.add_category(category_name)
            # Find the first empty product_id
            rows = app.db.execute('''
                SELECT product_id + 1 AS next_id
                FROM Products p1
                WHERE NOT EXISTS (
                    SELECT 1 
                    FROM Products p2 
                    WHERE p2.product_id = p1.product_id + 1
                )
                ORDER BY product_id
                LIMIT 1
            ''')
            next_product_id = rows[0][0] if rows else 1  # Start from 1 if the table is empty

            # Insert the new product
            app.db.execute('''
                INSERT INTO Products (product_id, category_name, name, description, image_url, price, created_by)
                VALUES (:product_id, :category_name, :name, :description, :image_url, :price, :created_by)
            ''', 
            product_id=next_product_id, 
            category_name=category_name,
            name=name,
            description=description,
            image_url=image_url,
            price=price,
            created_by=user_id)

            # Insert the new inventory
            app.db.execute('''
                INSERT INTO Inventory (seller_id, product_id, quantity)
                VALUES (:seller_id, :product_id, :quantity)
            ''', 
            seller_id=user_id, 
            product_id=next_product_id, 
            quantity=quantity)

            print("PRODUCTKLSJDFKLSDJFKLDSJFKLJDSKLFJSDKLFJSDKLJFSDFLKJDSFLSDSDLKFJDSKLFJ\nSDLKFJDSKLFJ", app.db.execute('''
            SELECT i.seller_id, i.quantity, i.product_id
            FROM Inventory i
            WHERE i.product_id = :product_id 
        ''', product_id=next_product_id))
            
            return True, next_product_id
        except Exception as e:
            print(f"Error adding product and inventory: {e}")
            return False, None
        
    @staticmethod
    def category_exists(category_name):
        rows = app.db.execute('''
            SELECT category_name FROM Categories WHERE category_name = :category_name
        ''', category_name=category_name)
        return len(rows) > 0

    @staticmethod
    def create_listing(seller_id, product_id, quantity):
        """
        Insert a new listing for an existing product into the Inventory table.
        """
        try:
            # Check if the seller already has an inventory entry for this product
            rows = app.db.execute('''
                SELECT inventory_id
                FROM Inventory
                WHERE seller_id = :seller_id AND product_id = :product_id
            ''', seller_id=seller_id, product_id=product_id)

            if rows:
                # Update existing inventory if it already exists
                app.db.execute('''
                    UPDATE Inventory
                    SET quantity = quantity + :quantity
                    WHERE seller_id = :seller_id AND product_id = :product_id
                ''', seller_id=seller_id, product_id=product_id, quantity=quantity)
            else:
                # Insert a new inventory record
                app.db.execute('''
                    INSERT INTO Inventory (seller_id, product_id, quantity)
                    VALUES (:seller_id, :product_id, :quantity)
                ''', seller_id=seller_id, product_id=product_id, quantity=quantity)

            return True
        except Exception as e:
            print(f"Error creating listing: {e}")
            return False

        
    @staticmethod
    def add_category(category_name):
        try:
            app.db.execute('''
                INSERT INTO Categories (category_name)
                VALUES (:category_name)
            ''', category_name=category_name)
        except Exception as e:
            print(f"Error adding category: {e}")

    @staticmethod
    def get_stock(product_id):
        rows = app.db.execute('''
            SELECT i.seller_id, i.quantity, u.full_name
            FROM Inventory i
            JOIN Users u ON i.seller_id = u.user_id
            WHERE i.product_id = :product_id 
        ''', product_id=product_id)
        print(rows)
        row = rows[0]
        return dict(seller_id=row[0], quantity=row[1], seller_name=row[2]) if rows else None
    # @staticmethod
    # def add_to_inventory(seller_id, product_id, quantity):
    #     try:
    #         app.db.execute('''
    #         INSERT INTO Inventory (seller_id, product_id, quantity)
    #         VALUES (:seller_id, :product_id, :quantity)
    #         RETURNING inventory_id
    #         ''', seller_id=seller_id, product_id=product_id, quantity=quantity)
    #         return {"product_id": product_id, "seller_id": seller_id, "quantity": quantity}
    #     except Exception as e:
    #         print(str(e))
    #         return None