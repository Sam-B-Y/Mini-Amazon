from flask import current_app as app


class Purchase:
    def __init__(self, order_id, user_id, product_id, ordered_time):
        self.order_id = order_id
        self.user_id = user_id
        self.product_id = product_id
        self.ordered_time = ordered_time

    @staticmethod
    def get(order_id):
        rows = app.db.execute('''
SELECT order_id, user_id, product_id, ordered_time
FROM orderitems
JOIN orders ON orders.order_id = orderitems.order_id
WHERE orderitems.order_id = :order_id
''',
                              order_id=order_id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_user_id_since(user_id: int, since: str) -> list['Purchase']:
        rows = app.db.execute('''
SELECT orderitems.order_id, user_id, product_id, ordered_time
FROM orderitems
JOIN orders ON orders.order_id = orderitems.order_id
WHERE user_id = :user_id
AND ordered_time >= :since
ORDER BY ordered_time DESC
''',
                              user_id=user_id,
                              since=since)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_orders_by_seller(seller_id: int, search_query: str = "", status_filter: str = "") -> list[dict]:
        rows = app.db.execute('''
            SELECT 
                oi.order_id,
                SUM(oi.quantity) AS total_quantity,  -- Aggregate quantity
                SUM(oi.unit_price * oi.quantity) AS total_price,  -- Aggregate total price
                o.ordered_time,
                u.full_name AS buyer_name,
                u.address AS buyer_address,
                o.status AS order_status,
                u.user_id AS buyer_id,
                -- Check if all order_items for the order are complete
                CASE WHEN COUNT(oi.status) FILTER (WHERE oi.status != 'Complete') = 0 THEN TRUE ELSE FALSE END AS completion_status
            FROM orderitems oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN users u ON o.user_id = u.user_id
            WHERE oi.seller_id = :seller_id
            AND (
                o.order_id::TEXT ILIKE :search_query OR
                u.full_name ILIKE :search_query OR
                u.address ILIKE :search_query
            )
            GROUP BY oi.order_id, o.ordered_time, u.full_name, u.address, o.status, u.user_id
            ORDER BY o.ordered_time DESC;
        ''', seller_id=seller_id, search_query=f"%{search_query}%")

        return [
            {
                "order_id": row[0],
                "quantity": row[1],
                "total_price": row[2],  # Total price from aggregation
                "ordered_time": row[3],
                "buyer_name": row[4],
                "buyer_address": row[5],
                "order_status": row[6],
                "buyer_id": row[7],
                "completion_status": row[8],  # True if all related order_items are complete
            }
            for row in rows if status_filter == "" or row[6] == status_filter
        ]




    @staticmethod
    def mark_order_as_complete(order_id: int, seller_id: int) -> bool:
        try:
            # Execute the update query
            rows_affected = app.db.execute('''
            UPDATE orders
            SET status = 'Complete'
            WHERE order_id = :order_id
            AND order_id IN (
                SELECT DISTINCT order_id
                FROM orderitems
                WHERE seller_id = :seller_id
            )
            ''', order_id=order_id, seller_id=seller_id)

            # Check if any rows were updated
            return rows_affected > 0
        except Exception as e:
            print(f"Error marking order as complete: {e}")
            return False

    @staticmethod
    def get_line_item_status(order_id, product_id, seller_id):
        """Fetch the current status of a specific line item."""
        rows = app.db.execute('''
            SELECT status
            FROM orderitems
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
        ''', order_id=order_id, product_id=product_id, seller_id=seller_id)
        
        return rows[0][0] if rows else None


    @staticmethod
    def mark_line_item_complete(order_id, product_id, seller_id):
        """Mark a specific line item as complete."""
        rows_affected = app.db.execute('''
            UPDATE orderitems
            SET status = 'Complete'
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
        ''', order_id=order_id, product_id=product_id, seller_id=seller_id)

        return rows_affected > 0
    

    @staticmethod
    def update_order_status_if_complete(order_id):
        """Check if all items in the order are complete and update the order's status."""
        try:
            # Check if all items for the given order_id are marked as 'Complete'
            rows = app.db.execute('''
                SELECT COUNT(*)
                FROM orderitems
                WHERE order_id = :order_id AND status != 'Complete'
            ''', order_id=order_id)

            # If no items are pending, mark the order as 'Complete'
            if rows[0][0] == 0:
                app.db.execute('''
                    UPDATE orders
                    SET status = 'Complete'
                    WHERE order_id = :order_id
                ''', order_id=order_id)
                return True  # Indicate that the order was marked as complete
            return False  # Indicate that the order remains incomplete
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False

    @staticmethod
    def update_line_item_status(order_id, product_id, seller_id, new_status):
        """Update the status of a specific line item."""
        try:
            rows_affected = app.db.execute('''
                UPDATE orderitems
                SET status = :new_status
                WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
            ''', order_id=order_id, product_id=product_id, seller_id=seller_id, new_status=new_status)
            return rows_affected > 0
        except Exception as e:
            print(f"Error updating line item status: {e}")
            return False
        

    @staticmethod
    def get_line_items(order_id: int, seller_id: int = None) -> list[dict]:
        """
        Fetch all line items for a specific order. If seller_id is provided, filter by seller_id.
        """
        try:
            query = '''
                SELECT 
                    product_id,
                    quantity,
                    unit_price,
                    status
                FROM orderitems
                WHERE order_id = :order_id
            '''
            params = {"order_id": order_id}

            # Add seller_id filter if provided
            if seller_id is not None:
                query += " AND seller_id = :seller_id"
                params["seller_id"] = seller_id

            rows = app.db.execute(query, **params)
            
            # Return as a list of dictionaries
            return [
                {
                    "product_id": row[0],
                    "quantity": row[1],
                    "unit_price": row[2],
                    "status": row[3],
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error fetching line items: {e}")
            return []
    @staticmethod
    def get_order_items_by_seller(seller_id, search_query="", status_filter="All"):
        try:
            print("yay")
            query = '''
                SELECT oi.order_id, oi.product_id, oi.quantity, oi.unit_price, oi.status,
                    o.ordered_time, u.full_name AS buyer_name, u.address AS buyer_address
                FROM orderitems oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN users u ON o.user_id = u.user_id
                WHERE oi.seller_id = :seller_id
            '''
            params = {"seller_id": seller_id}

            # Apply status filtering
            if status_filter != "All":
                query += " AND oi.status = :status"
                params["status"] = status_filter

            # Apply search filtering
            if search_query:
                query += '''
                    AND (
                        oi.order_id::TEXT ILIKE :search_query OR
                        u.full_name ILIKE :search_query OR
                        u.address ILIKE :search_query
                    )
                '''
                params["search_query"] = f"%{search_query}%"

            rows = app.db.execute(query, **params)

            return [
                {
                    'order_id': row[0],
                    'product_id': row[1],
                    'quantity': row[2],
                    'unit_price': row[3],
                    'status': row[4],
                    'ordered_time': row[5],
                    'buyer_name': row[6],
                    'buyer_address': row[7]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error fetching order items by seller: {e}")
            return []
