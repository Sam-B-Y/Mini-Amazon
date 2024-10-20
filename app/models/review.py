from flask import current_app as app

class Review:
    def __init__(self, review_id, user_id, product_id, seller_id, rating, comment, added_at):
        self.review_id = review_id
        self.user_id = user_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.rating = rating
        self.comment = comment
        self.added_at = added_at

    @staticmethod
    def get_product_reviews(product_id, seller_id):
        rows = app.db.execute('''
SELECT *
FROM reviews
WHERE product_id = :product_id AND seller_id = :seller_id
''', 
                              product_id=product_id, seller_id = seller_id)
        return [Review(*row) for row in rows]
        
    @staticmethod
    def get_recent(user_id):
        rows = app.db.execute('''
SELECT *
FROM Reviews
WHERE user_id = :user_id
ORDER BY added_at DESC limit 5
''', user_id=user_id)
        return [Review(*row) for row in rows]
