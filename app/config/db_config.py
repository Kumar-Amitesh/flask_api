import os
# from psycopg2 import pool
import psycopg2
from pymongo import MongoClient

# pg_pool = pool.SimpleConnectionPool(
#     minconn=1,
#     maxconn=10,
#     dsn=os.getenv("DATABASE_URL")
# )

# PostgreSQL Connection
def get_pg_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None


# MongoDB Connection
def get_mongo_db():
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        # Returns the default database from the URI
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# Initialize MongoDB instance once
# mongo_db = get_mongo_db()

# db = mongo_db["data"]
# product_collection = db["product_data"]

def init_db():
    conn = get_pg_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(150) UNIQUE NOT NULL,
                phone_number VARCHAR(20),
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cur.close()
        conn.close()
