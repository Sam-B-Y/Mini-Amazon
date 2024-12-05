import pandas as pd
import json
import random

original_csv_path = "../data/Products.csv"
original_data = pd.read_csv(original_csv_path)

amazon_csv_path = "amazon-products.csv"
amazon_data = pd.read_csv(amazon_csv_path)

required_columns = {
    'categories': 'category_name',
    'title': 'name',
    'description': 'description',
    'image_url': 'image_url',
    'final_price': 'price'
}
amazon_data = amazon_data[list(required_columns.keys())]
amazon_data.rename(columns=required_columns, inplace=True)

# if final_price is empty create a random number between 10 and 35
amazon_data['price'] = amazon_data['price'].apply(lambda x: float(str(x).replace('"', "").replace(",", "")))
amazon_data['price'] = amazon_data['price'].fillna(0)
amazon_data['price'] = amazon_data['price'].apply(lambda x: x if x != 0 else round(10 + (35 - 10) * random.random(), 2))

amazon_data['name'] = amazon_data['name'].apply(lambda x: x[:250])

print(amazon_data.isnull().sum())

amazon_data['image_url'].fillna('https://via.placeholder.com/150', inplace=True)
amazon_data['description'].fillna('No description available', inplace=True)

if len(original_data) != len(amazon_data):
    original_data = original_data[:len(amazon_data)]


updated_data = original_data[['product_id', 'created_by']].copy()
updated_data = pd.concat([updated_data, amazon_data], axis=1)

print(updated_data.head())

def test(x):
    try:
        temp = json.loads(x)
        return temp[0]
    except:
        return x

updated_data['category_name'] = updated_data['category_name'].apply(lambda x: test(x))

updated_data['product_id'] = updated_data['product_id'].astype(int)
updated_data['created_by'] = updated_data['created_by'].astype(int)

# reorder columns to be  product_id | category_name | name | description | image_url | price | created_by 
updated_data = updated_data[['product_id', 'category_name', 'name', 'description', 'image_url', 'price', 'created_by']]

output_csv_path = "../data/Products.csv"
updated_data.to_csv(output_csv_path, index=False)

print(f"Updated dataset saved to {output_csv_path}")

# get all unique categories
categories = updated_data['category_name'].unique()

# save categories to categories.csv
categories_df = pd.DataFrame(categories, columns=['category_name'])
categories_df.to_csv('../data/categories.csv', index=False)