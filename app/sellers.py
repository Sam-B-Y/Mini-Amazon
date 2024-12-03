from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Connect to PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="your_host",
        database="your_database",
        user="your_username",
        password="your_password"
    )
    return conn

