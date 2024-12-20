CREATE TABLE Users (
    user_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    is_seller BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Categories (
    category_name VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY
);

CREATE TABLE Products (
    product_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    category_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(500),
    price DECIMAL(10,2) NOT NULL,
    created_by INT NOT NULL,
    FOREIGN KEY (category_name) REFERENCES Categories(category_name),
    FOREIGN KEY (created_by) REFERENCES Users(user_id)
);

CREATE TABLE Inventory (
    inventory_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    seller_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (seller_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    UNIQUE (seller_id, product_id)
);

CREATE TABLE CartItems (
    cart_item_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (seller_id) REFERENCES Users(user_id),
    UNIQUE (user_id, product_id, seller_id)
);

CREATE TABLE Orders (
    order_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    ordered_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


CREATE TABLE Coupons (
    coupon_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    categories VARCHAR(255) NOT NULL,
    discount INT NOT NULL,
    expiry_date DATE NOT NULL
);

CREATE TABLE AppliedCoupons (
    user_id INT NOT NULL,
    coupon_id INT NOT NULL,
    cart BOOLEAN NOT NULL DEFAULT FALSE,
    order_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES Coupons(coupon_id),
    PRIMARY KEY (user_id, coupon_id)
);


CREATE TABLE OrderItems (
    order_item_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Ordered',
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (seller_id) REFERENCES Users(user_id),
    UNIQUE (order_id, product_id, seller_id)
);

CREATE TABLE Reviews (
    review_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL,
    product_id INT,
    seller_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (seller_id) REFERENCES Users(user_id)
);
