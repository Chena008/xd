import os
from dotenv import load_dotenv
from flask import request, jsonify
import sqlite3
import requests

load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")

def product_exists(product_id):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}",headers={"Authorization":"Bearer token_service"}, timeout=5)

        return response.status_code == 200

    except requests.RequestException:
        return False

def inventory_exists(product_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT product_id FROM inventory WHERE product_id = ?",
        (product_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row is not None