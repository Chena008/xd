import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "products.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM products")
    rows = cursor.fetchall()

    conn.close()

    return rows


def get_product_by_id_db(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM products WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def create_product_db(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO products (name) VALUES (?)",
        (name,)
    )

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return new_id


def update_product_db(id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE products SET name = ? WHERE id = ?",
        (name, id)
    )

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    return updated


def delete_product_db(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (id,)
    )

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    return deleted