import pandas as pd

previous = '../data/Products.csv'
kaggleNewData = './kaggleProductData.csv'

existing_df = pd.read_csv(previous)
existing_df['product_id'] = pd.to_numeric(existing_df['product_id'], errors='coerce')
existing_df = existing_df.dropna(subset=['product_id'])
existing_df['product_id'] = existing_df['product_id'].astype(int)

if not existing_df.empty:
    last_product_id = existing_df['product_id'].max()
else:
    last_product_id = 0 

kaggle_df = pd.read_csv(kaggleNewData)
kaggle_df = kaggle_df.rename(columns={
    'S.No': 'product_id',             
    'Category': 'category_name',      
    'Product Name': 'name',           
    'Brand Desc': 'description' 
})

kaggle_df = kaggle_df[['product_id', 'category_name', 'name', 'description']]

kaggle_df['image_url'] = 'https://example.com/image.jpg'
kaggle_df['price'] = None
kaggle_df['created_by'] = None

kaggle_df['product_id'] += last_product_id
kaggle_df = kaggle_df[['product_id', 'category_name', 'name', 'description', 'image_url', 'price', 'created_by']]
combined_df = pd.concat([existing_df, kaggle_df], ignore_index=True)
combined_df.to_csv(previous, index=False)
