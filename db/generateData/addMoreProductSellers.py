import csv
import random

# File paths
inventory_csv_path = "../data/inventory.csv"
users_csv_path = "../data/Users.csv"

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

# Generate new inventory entries
def generate_inventory_entries(existing_inventory, sellers, num_entries_to_add=5):
    # Find the last inventory_id
    last_inventory_id = max(int(item["inventory_id"]) for item in existing_inventory)

    new_inventory = []
    for i in range(num_entries_to_add):
        existing_product = random.choice(existing_inventory)  # Randomly select an existing product
        new_inventory_id = last_inventory_id + i + 1  # Increment inventory_id
        new_seller_id = random.choice(sellers)["user_id"]  # Randomly select a valid seller_id
        new_quantity = random.randint(1, 50)  # Generate a random quantity

        # Create new inventory entry
        new_inventory.append({
            "inventory_id": new_inventory_id,
            "seller_id": new_seller_id,
            "product_id": existing_product["product_id"],
            "quantity": new_quantity
        })

    return new_inventory

# Sanitize and filter duplicates based on `product_id` and `seller_id`
def sanitize_and_filter_duplicates(file_path):
    with open(file_path, mode="r") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)  # Read all rows into memory

        # Sanitize and remove duplicates based on `product_id` and `seller_id`
        seen = set()
        unique_rows = []
        for row in rows:
            # Replace any carriage returns or newlines in fields
            sanitized_row = {k: v.replace("\r", " ").replace("\n", " ") for k, v in row.items()}
            key = (sanitized_row["product_id"], sanitized_row["seller_id"])  # Use product_id and seller_id as key
            if key not in seen:
                seen.add(key)
                unique_rows.append(sanitized_row)

    # Write sanitized and filtered rows back to the file
    with open(file_path, mode="w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

# Main script logic
if __name__ == "__main__":
    # Step 1: Read the existing CSVs
    inventory = read_csv(inventory_csv_path)
    users = read_csv(users_csv_path)

    # Step 2: Filter valid sellers from Users.csv
    sellers = [user for user in users if user["is_seller"].lower() == "true"]

    if not sellers:
        print("No valid sellers found in Users.csv.")
        exit()

    # Step 3: Generate new inventory entries
    new_inventory = generate_inventory_entries(inventory, sellers, num_entries_to_add=2000)

    # Step 4: Append new inventory entries to the inventory.csv
    fieldnames = inventory[0].keys()  # Use existing fieldnames
    append_to_csv(inventory_csv_path, fieldnames, new_inventory)

    print(f"Added {len(new_inventory)} new inventory entries to {inventory_csv_path}.")

    # Step 5: Sanitize and filter duplicates
    sanitize_and_filter_duplicates(inventory_csv_path)

    print(f"Sanitized and filtered duplicates in {inventory_csv_path}.")




