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
                              product_id=product_id, seller_id=seller_id)
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

    @staticmethod
    def get_seller_reviews(seller_id):
        rows = app.db.execute('''
        SELECT reviews.*, users.full_name
        FROM Reviews
        JOIN users ON reviews.user_id = users.user_id
        WHERE seller_id = :seller_id
        ORDER BY added_at DESC
        ''', seller_id=seller_id)
        return rows
    
    def submit_review(user_id, product_id, seller_id, rating, comment):
        existing_review = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id AND seller_id = :seller_id
''', user_id=user_id, seller_id=seller_id)

        if existing_review:
            raise Exception("User has already submitted a review for this seller.")

        app.db.execute('''
INSERT INTO reviews (user_id, product_id, seller_id, rating, comment, added_at)
VALUES (:user_id, :product_id, :seller_id, :rating, :comment, CURRENT_TIMESTAMP)
''', user_id=user_id, product_id=product_id, seller_id=seller_id, rating=rating, comment=comment)

    @staticmethod
    def edit_review(review_id, rating, comment):
        app.db.execute('''
UPDATE reviews
SET rating = :rating, comment = :comment
WHERE review_id = :review_id
''', review_id=review_id, rating=rating, comment=comment)

    @staticmethod
    def remove_review(review_id):
        app.db.execute('''
DELETE FROM reviews
WHERE review_id = :review_id
''', review_id=review_id)

    @staticmethod
    def get_my_reviews(user_id):
        rows = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id
''', user_id=user_id)
        return [Review(*row) for row in rows]