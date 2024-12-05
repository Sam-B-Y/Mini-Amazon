import csv
import random

# File paths
products_csv_path = "../data/Products.csv"
order_items_csv_path = "../data/order_items.csv"

# Function to read CSV into a list of dictionaries
def read_csv(file_path):
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to append rows to a CSV
def append_to_csv(file_path, fieldnames, rows):
    with open(file_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerows(rows)

# Generate new order_items with random order_ids
def generate_order_items(products, order_items, num_items_to_add=1000):
    # Find the last order_item_id
    last_order_item_id = max(int(item["order_item_id"]) for item in order_items)

    new_order_items = []
    for i in range(num_items_to_add):
        product = random.choice(products)  # Randomly select a product
        quantity = random.randint(1, 10)  # Random quantity between 1 and 10
        new_order_item_id = last_order_item_id + i + 1  # Increment order_item_id
        new_order_id = random.randint(1, 1000)  # Random order_id between 1 and 1000

        # Create new order item row
        new_order_items.append({
            "order_item_id": new_order_item_id,
            "order_id": new_order_id,
            "product_id": product["product_id"],
            "seller_id": product["created_by"],
            "quantity": quantity,
            "unit_price": product["price"]
        })

    return new_order_items

# Main script logic
if __name__ == "__main__":
    # Step 1: Read the existing CSVs
    products = read_csv(products_csv_path)
    order_items = read_csv(order_items_csv_path)

    # Step 2: Generate new order items
    new_order_items = generate_order_items(products, order_items, num_items_to_add=1000)

    # Step 3: Append new order items to the order_items.csv
    fieldnames = order_items[0].keys()  # Use existing fieldnames
    append_to_csv(order_items_csv_path, fieldnames, new_order_items)

    print(f"Added {len(new_order_items)} new order items to {order_items_csv_path}.")
