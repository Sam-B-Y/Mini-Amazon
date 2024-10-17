\COPY Users FROM 'users.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.users_user_id_seq',
                         (SELECT MAX(user_id)+1 FROM Users),
                         false);

\COPY Categories FROM 'categories.csv' WITH DELIMITER ',' NULL '' CSV HEADER;

\COPY Products FROM 'products.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.products_product_id_seq',
                         (SELECT MAX(product_id)+1 FROM Products),
                         false);

\COPY Inventory FROM 'inventory.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.inventory_inventory_id_seq',
                         (SELECT MAX(inventory_id)+1 FROM Inventory),
                         false);

\COPY CartItems FROM 'cart_items.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.cartitems_cart_item_id_seq',
                         (SELECT MAX(cart_item_id)+1 FROM CartItems),
                         false);

\COPY Orders FROM 'orders.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.orders_order_id_seq',
                         (SELECT MAX(order_id)+1 FROM Orders),
                         false);

\COPY OrderItems FROM 'order_items.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.orderitems_order_item_id_seq',
                         (SELECT MAX(order_item_id)+1 FROM OrderItems),
                         false);

\COPY Reviews FROM 'reviews.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.reviews_review_id_seq',
                         (SELECT MAX(review_id)+1 FROM Reviews),
                         false);
