'''
Data generator CLEARS ALL DATA in existing CSVs (except Users) and regenerates it.
'''

import csv
from os import listdir, getcwd
from os.path import isfile, join
from faker import Faker
import pandas as pd
import numpy as np
import datetime
import random

Faker.seed(0)
fake = Faker()

num_cart_items = 500
num_reviews = 3000
num_orders = 5000

kaggleNewData = 'db/generateData/kaggleProductData.csv'

# get user data

users = pd.read_csv("db/data/Users.csv")
sellers = users[users["is_seller"] == True]

kaggle_df = pd.read_csv(kaggleNewData)
kaggle_df = kaggle_df.rename(columns={
    'S.No': 'product_id',             
    'Category': 'category_name',      
    'Product Name': 'name',           
    'Brand Desc': 'description' 
})
kaggle_df["image_url"] = "https://picsum.photos/id/0/200/300"
kaggle_df["price"] = [float(fake.random_int(max=10000) + fake.random_int(max=99) * 0.01) for i in range(len(kaggle_df))]
kaggle_df["created_by"] = [sellers.sample(n=1).iloc[0]["user_id"] for i in range(len(kaggle_df))]
kaggle_df["quantity"] = [np.random.randint(20, 100) for i in range(len(kaggle_df))]
kaggle_df["inventory_id"] = [i + 1 for i in range(len(kaggle_df))]
kaggle_df = kaggle_df.replace(',','', regex=True)
# make categories table

categories = kaggle_df["category_name"].drop_duplicates()
categories.to_csv("db/data/categories.csv", index=False)

# make products table
products = kaggle_df[['product_id', 'category_name', 'name', 'description', 'image_url', 'price', 'created_by']]
products.to_csv("db/data/Products.csv", index=False)

# make orders table, keeping a constant list of users who ordered stuff and products ordered

users_who_ordered = [np.random.randint(1, len(users)) for i in range(num_orders)]
seller_list = sellers.sample(n=num_orders, replace=True)
seller_id_list = [seller_list.iloc[i]["user_id"] for i in range(len(seller_list))]
products_ordered = [np.random.randint(1, len(products)) for i in range(num_orders)]
prices = [products.iloc[products_ordered[i]]["price"] for i in range(len(products_ordered))]

statuses = ["Pending", "Complete"]

start_time = "05-01-2008 12:00:00"
end_time = "05-01-2015 12:00:00"
frmt = '%m-%d-%Y %H:%M:%S'
stime = datetime.datetime.strptime(start_time, frmt)
etime = datetime.datetime.strptime(end_time, frmt)
td = etime - stime

orders = pd.read_csv("db/data/orders.csv")
orders = orders[0:0] 

orders["order_id"] = [i + 1 for i in range(num_orders)]
orders["user_id"] = users_who_ordered
orders["status"] = [statuses[np.random.randint(0, 2)] for i in range(num_orders)]
orders["ordered_time"] = [(random.random() * td + stime).strftime("%Y-%m-%d %H:%M:%S") for i in range(num_orders)]

orders.to_csv("db/data/orders.csv", index=False)

# make reviews table, making sure that reviews are generated after orders, only taking the first num_reviews products

start_time = "05-01-2015 12:00:00"
end_time = "05-01-2024 12:00:00"
frmt = '%m-%d-%Y %H:%M:%S'
stime = datetime.datetime.strptime(start_time, frmt)
etime = datetime.datetime.strptime(end_time, frmt)
td = etime - stime

reviews = pd.read_csv("db/data/reviews.csv")
reviews = reviews[0:0] 

reviews["review_id"] = [i + 1 for i in range(num_reviews)]
reviews["user_id"] = users_who_ordered[:num_reviews]
reviews["product_id"] = products_ordered[:num_reviews]
reviews["seller_id"] = seller_id_list[:num_reviews]
reviews["rating"] = [np.random.randint(1, 6) for i in range(num_reviews)]
reviews["comment"] = [fake.sentence(nb_words=10) for i in range(num_reviews)]
reviews["added_at"] = [(random.random() * td + stime).strftime("%Y-%m-%d %H:%M:%S") for i in range(num_reviews)]

reviews.to_csv("db/data/reviews.csv", index=False)

# make order_items table

order_items = pd.read_csv("db/data/order_items.csv")
order_items = order_items[0:0] 

quantities = [np.random.randint(1, 20) for i in range(num_orders)]

order_items["order_item_id"] = [i + 1 for i in range(num_orders)]
order_items["order_id"] = [i + 1 for i in range(num_orders)]
order_items["product_id"] = products_ordered
order_items["seller_id"] = seller_id_list
order_items["quantity"] = quantities
order_items["unit_price"] = [round(prices[i]/quantities[i], 2) for i in range(num_orders)]

order_items.to_csv("db/data/order_items.csv", index=False)

# make cart_items table

cart_items = pd.read_csv("db/data/cart_items.csv")
cart_items = cart_items[0:0] 

cart_products = [np.random.randint(1, len(products)) for i in range(num_cart_items)]

start_time = "05-01-2023 12:00:00"
end_time = "05-01-2024 12:00:00"
frmt = '%m-%d-%Y %H:%M:%S'
stime = datetime.datetime.strptime(start_time, frmt)
etime = datetime.datetime.strptime(end_time, frmt)
td = etime - stime

cart_items["cart_item_id"] = [i + 1 for i in range(num_cart_items)]
cart_items["user_id"] = [np.random.randint(1, len(users)) for i in range(num_cart_items)]
cart_items["product_id"] = cart_products
cart_items["seller_id"] = [products.iloc[cart_products[i]]["created_by"] for i in range(num_cart_items)]
cart_items["quantity"] = [np.random.randint(1, 20) for i in range(num_cart_items)]
cart_items["added_at"] = [(random.random() * td + stime).strftime("%Y-%m-%d %H:%M:%S") for i in range(num_cart_items)]

cart_items.to_csv("db/data/cart_items.csv", index=False)

# make inventory table

inventory = pd.read_csv("db/data/inventory.csv")
inventory = inventory[0:0] 

kaggle_df = kaggle_df.rename(columns={
    'created_by': 'seller_id',       
})

inventory = kaggle_df[['inventory_id', 'seller_id', 'product_id', 'quantity']]

inventory.to_csv("db/data/inventory.csv", index=False)