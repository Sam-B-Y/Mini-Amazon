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
FROM OrderItems
JOIN Orders ON Orders.order_id = OrderItems.order_id
WHERE OrderItems.order_id = :order_id
''',
                              order_id=order_id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_user_id_since(user_id, since):
        rows = app.db.execute('''
SELECT OrderItems.order_id, user_id, product_id, ordered_time
FROM OrderItems
JOIN Orders ON Orders.order_id = OrderItems.order_id
WHERE user_id = :user_id
AND ordered_time >= :since
ORDER BY ordered_time DESC
''',
                              user_id=user_id,
                              since=since)
        return [Purchase(*row) for row in rows]
