import os
from dotenv import load_dotenv
import sqlite3
import requests
from auth import authorize
from app import app
from flask import request, jsonify


load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def product_exists(product_id):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}",
                                headers={'Authorization':'Bearer token_service'},
                                timeout=5)

        return response.status_code == 200

    except requests.RequestException:
        return False

def get_inventory(product_id):
    try:
        response = requests.get(
            f"{INVENTORY_SERVICE_URL}/inventory/{product_id}",
            headers={'Authorization':'Bearer token_service'},
            timeout=5
        )

        return response

    except requests.RequestException:
        return None

def reserve_inventory(product_id, quantity):
    try:
        response = requests.post(
            f"{INVENTORY_SERVICE_URL}/inventory/{product_id}/reserve",
            json={"quantity": quantity},
            headers={
                "Authorization":"Bearer token_service"
            },
            timeout=5
        )

        return response

    except requests.RequestException:
        return None

@app.route("/orders", methods=["GET"])
def get_orders():

    auth_data, error = authorize(["admin", "service"])

    if error:
        return error

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, product_id, quantity, status FROM orders")
    rows = cursor.fetchall()

    conn.close()

    orders = []

    for row in rows:
        orders.append({
            "id": row[0],
            "product_id": row[1],
            "quantity": row[2],
            "status": row[3]
        })

    return jsonify(orders), 200

@app.route("/orders", methods=["POST"])
def crear_pedido():

    auth_data, error = authorize(["admin"])

    if error:
        return error

    data = request.get_json()

    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "Faltan campos product_id y quantity"}), 400

    product_id = data["product_id"]
    quantity = data["quantity"]

    if quantity <= 0:
        return jsonify({"error":"La cantidad debe ser mayor a cero."}), 400
    
    if not product_exists(product_id):
        return jsonify({"error": "El producto no existe en product-service"}), 404
    
    inventory_response = get_inventory(product_id)

    if inventory_response is None:
        return jsonify({
            "error": "inventory-service no está disponible"
        }), 503

    if inventory_response.status_code == 404:
        return jsonify({
            "error": "Ese producto no tiene inventario"
        }), 404

    if inventory_response.status_code != 200:
        return jsonify({
            "error": "Error al consultar inventory-service"
        }), inventory_response.status_code

    inventory = inventory_response.json()

    stock_disponible = inventory["stock"]

    if stock_disponible < quantity:
        return jsonify({
            "error": "Stock insuficiente",
            "stock_disponible": stock_disponible,
            "quantity_solicitada": quantity
        }), 400
    
    reservation = reserve_inventory(product_id, quantity)

    if reservation is None:
        return jsonify({
            "error": "inventory-service no está disponible"
        }), 503

    if reservation.status_code != 200:
        return jsonify(reservation.json()), reservation.status_code

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO orders (product_id, quantity, status) VALUES (?, ?, ?)",
        (product_id, quantity, "CREATED")
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": new_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "CREATED"
    }), 201

@app.route("/orders/<int:id>", methods=["GET"])
def get_order_by_id(id):
    auth_data, error = authorize(["admin", "service"])

    if error:
        return error

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, product_id, quantity, status FROM orders WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Pedido no encontrado"}), 404

    return jsonify({
        "id": row[0],
        "product_id": row[1],
        "quantity": row[2],
        "status": row[3]
    }), 200