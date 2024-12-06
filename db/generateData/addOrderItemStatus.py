import csv
import random

def update_order_items_status_in_place(order_items_file_path, orders_file_path):
    # Define possible statuses
    statuses = ["Ordered", "Pending", "Complete"]
    
    # Load orders marked as complete
    completed_orders = set()
    with open(orders_file_path, mode='r') as orders_file:
        orders_reader = csv.DictReader(orders_file)
        for order_row in orders_reader:
            if order_row['status'] == 'Complete':
                completed_orders.add(order_row['order_id'])

    # Read and update order items
    with open(order_items_file_path, mode='r') as order_items_file:
        order_items_reader = csv.DictReader(order_items_file)
        rows = list(order_items_reader)  # Read all rows into memory
        
        # Update the status field for each row
        for row in rows:
            if row['order_id'] in completed_orders:
                row['status'] = 'Complete'  # Force complete if the order is complete
            else:
                row['status'] = random.choice(statuses)  # Assign random status otherwise
    
    # Write updated rows back to the same file
    with open(order_items_file_path, mode='w', newline='') as order_items_file:
        # Get fieldnames from the original file
        fieldnames = order_items_reader.fieldnames
        writer = csv.DictWriter(order_items_file, fieldnames=fieldnames)
        
        # Write header and updated rows
        writer.writeheader()
        writer.writerows(rows)

# File paths
order_items_file_path = '../data/order_items.csv'
orders_file_path = '../data/orders.csv'

# Update the CSV with random statuses
update_order_items_status_in_place(order_items_file_path, orders_file_path)

print(f"Updated statuses in {order_items_file_path} based on {orders_file_path}.")
