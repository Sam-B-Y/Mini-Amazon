import csv
import random

def update_order_items_status_in_place(file_path):
    # Define possible statuses
    statuses = ["Complete", "Pending"]
    
    # Read the original file and update rows in memory
    with open(file_path, mode='r') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)  # Read all rows into memory
        
        # Update the status field for each row
        for row in rows:
            row['status'] = random.choice(statuses)
    
    # Write updated rows back to the same file
    with open(file_path, mode='w', newline='') as outfile:
        # Get fieldnames from the original file
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        # Write header and updated rows
        writer.writeheader()
        writer.writerows(rows)

# File path
file_path = '../data/order_items.csv'

# Update the CSV with random statuses
update_order_items_status_in_place(file_path)

print(f"Updated statuses in {file_path}.")
