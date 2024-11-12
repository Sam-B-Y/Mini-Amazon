import csv
import random
from faker import Faker
import hashlib
import os
import secrets

# Initialize Faker
fake = Faker()

# Specify the number of users to generate
num_users = 100  # Adjust this number as needed

# Relative file path
output_file = os.path.join('db', 'data', 'Users.csv')

# Create the directory if it does not exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Function to generate a password hash similar to pbkdf2:sha256
def generate_password_hash(password):
    salt = secrets.token_hex(16)
    hash_object = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000)
    return f"pbkdf2:sha256:600000${salt}${hash_object.hex()}"

# Determine the starting user_id by checking the highest existing user_id
start_id = 1
if os.path.isfile(output_file):
    with open(output_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # Check if the row is not empty
                try:
                    current_id = int(row[0])  # user_id is in the first column
                    start_id = max(start_id, current_id + 1)
                except ValueError:
                    continue  # Skip any rows with non-integer user_id (e.g., headers)

# Generate user data
user_data = []
for i in range(start_id, start_id + num_users):
    user_id = i
    email = fake.email()
    full_name = fake.name()
    address = fake.address().replace('\n', ', ')
    password = fake.password()
    password_hash = generate_password_hash(password)
    balance = round(random.uniform(0, 10000), 2)  # Random balance between 0 and 10,000
    is_seller = random.choice([True, False])  # Randomly assign as seller or not

    user_data.append([
        user_id,
        email,
        full_name,
        address,
        password_hash,
        balance,
        is_seller
    ])

# Write to CSV without headers
with open(output_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(user_data)

print(f"Appended {num_users} new users to {output_file} starting from user_id {start_id}")
