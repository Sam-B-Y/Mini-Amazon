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
            oi.quantity,
            oi.unit_price,
            o.ordered_time,
            u.full_name AS buyer_name,
            u.address AS buyer_address,
            o.status AS order_status,
            u.user_id AS buyer_id
        FROM orderitems oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN users u ON o.user_id = u.user_id
        WHERE oi.seller_id = :seller_id
        AND (
            o.order_id::TEXT ILIKE :search_query OR
            u.full_name ILIKE :search_query OR
            u.address ILIKE :search_query
        )
        ORDER BY o.ordered_time DESC;
        ''', seller_id=seller_id, search_query=f"%{search_query}%")

        return [
            {
                "order_id": row[0],
                "quantity": row[1],
                "unit_price": row[2],
                "ordered_time": row[3],
                "buyer_name": row[4],
                "buyer_address": row[5],
                "order_status": row[6],
                "buyer_id": row[7]
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

