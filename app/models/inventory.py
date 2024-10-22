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
                p.name AS product_name, p.description, p.image_url, p.price
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
            price=row[7]
        ) for row in rows] if rows else []


    

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