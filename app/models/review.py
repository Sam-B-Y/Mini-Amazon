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
ORDER BY added_at DESC 
''', user_id=user_id)
        return [Review(*row) for row in rows]

    @staticmethod
    def get_seller_reviews(seller_id):
        rows = app.db.execute('''
        SELECT reviews.*, users.full_name
        FROM Reviews
        JOIN users ON reviews.user_id = users.user_id
        WHERE seller_id = :seller_id AND product_id IS NULL
        ORDER BY added_at DESC
        ''', seller_id=seller_id)
        return rows
    
    @staticmethod
    def submit_product_review(user_id, product_id, seller_id, rating, comment):
        existing_review = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id AND product_id = :product_id
''', user_id=user_id, seller_id=seller_id, product_id=product_id)

        if existing_review:
            raise Exception("User has already submitted a review for this product.")

        app.db.execute('''
INSERT INTO reviews (user_id, product_id, seller_id, rating, comment, added_at)
VALUES (:user_id, :product_id, :seller_id, :rating, :comment, CURRENT_TIMESTAMP)
''', user_id=user_id, product_id=product_id, seller_id=seller_id, rating=rating, comment=comment)

    @staticmethod
    def submit_seller_review(user_id, seller_id, rating, comment):
        # Check if the user has purchased from the seller
        purchases = app.db.execute('''
SELECT DISTINCT o.order_id
FROM orders o
JOIN OrderItems oi ON o.order_id = oi.order_id
WHERE o.user_id = :user_id
AND oi.seller_id = :seller_id;
''', user_id=user_id, seller_id=seller_id)

        if not purchases:
            raise Exception("User must have purchased a product from this seller to submit a review.")
        same_seller_review = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id AND seller_id = :seller_id AND user_id = seller_id
''', user_id=user_id, seller_id=seller_id)
        if same_seller_review:
            raise Exception("User cannot submit a review for themselves.")
        
        existing_review = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id AND seller_id = :seller_id AND product_id IS NULL
''', user_id=user_id, seller_id=seller_id)

        if existing_review:
            raise Exception("User has already submitted a review for this seller.")
        

        app.db.execute('''
INSERT INTO reviews (user_id, seller_id, rating, comment, added_at)
VALUES (:user_id, :seller_id, :rating, :comment, CURRENT_TIMESTAMP)
''', user_id=user_id, seller_id=seller_id, rating=rating, comment=comment)

    @staticmethod
    def edit_review(review_id, rating, comment):
        app.db.execute('''
UPDATE reviews
SET rating = :rating, comment = :comment, added_at = CURRENT_TIMESTAMP
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
    
    @staticmethod
    def get_my_product_reviews(user_id):
        rows = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id AND product_id IS NOT NULL
                              ORDER BY added_at DESC
''', user_id=user_id)
        return [Review(*row) for row in rows]
    
    @staticmethod
    def get_my_seller_reviews(user_id):
        rows = app.db.execute('''
SELECT *
FROM reviews
WHERE user_id = :user_id AND product_id IS NULL
                              ORDER BY added_at DESC
''', user_id=user_id)
        return [Review(*row) for row in rows]
