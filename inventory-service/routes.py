import sqlite3
from repository import product_exists, inventory_exists
from auth import authorize
from app import app
from flask import request, jsonify

@app.route("/inventory", methods=["GET"])
def get_inventory():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT product_id, stock FROM inventory")
    rows = cursor.fetchall()

    conn.close()

    inventory = []

    for row in rows:
        inventory.append({
            "product_id": row[0],
            "stock": row[1]
        })

    return jsonify(inventory), 200

@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_inventory_by_product(product_id):
    auth_data, error = authorize(["admin", "service"])

    if error:
        return error

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT product_id, stock FROM inventory WHERE product_id = ?",
        (product_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Inventario no encontrado"}), 404

    return jsonify({
        "product_id": row[0],
        "stock": row[1]
    }), 200

@app.route("/inventory", methods=["POST"])
def create_inventory():

    auth_data, error = authorize(["admin"])

    if error:
        return error

    data = request.get_json()

    if not data or "product_id" not in data or "stock" not in data:
        return jsonify({"error": "Faltan campos product_id y stock"}), 400

    product_id = data["product_id"]
    stock = data["stock"]

    if stock < 0:
        return jsonify({"error": "El stock no puede ser negativo"}), 400

    if not product_exists(product_id):
        return jsonify({"error": "El producto no existe en product-service"}), 404
    
    if inventory_exists(product_id):
        return jsonify({"error": "Ese producto ya tiene inventario."}), 409

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO inventory (product_id, stock) VALUES (?, ?)",
        (product_id, stock)
    )

    conn.commit()
    conn.close()

    return jsonify({"product_id": product_id, "stock": stock}), 201

@app.route("/inventory/<int:product_id>", methods=["PUT"])
def update_inventory(product_id):

    auth_data, error = authorize(["admin"])

    if error:
        return error

    data = request.get_json()

    if not data or "stock" not in data:
        return jsonify({"error": "Falta el campo stock"}), 400

    stock = data["stock"]

    if stock < 0:
        return jsonify({"error": "El stock no puede ser negativo"}), 400

    if not product_exists(product_id):
        return jsonify({"error": "El producto no existe en product-service"}), 404

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE inventory SET stock = ? WHERE product_id = ?",
        (stock, product_id)
    )

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Inventario no encontrado para ese producto"}), 404

    conn.close()

    return jsonify({"product_id": product_id, "stock": stock}), 200

@app.route("/inventory/<int:product_id>/reserve", methods=["POST"])
def reserve_stock(product_id):

    auth_data, error = authorize(["admin"])

    if error:
        return error

    data = request.get_json()

    if not data or "quantity" not in data:
        return jsonify({"error":"Falta el campo quantity"}), 400
    
    quantity = data["quantity"]

    if quantity <= 0:
        return jsonify({"error":"La cantidad debe ser mayor a cero"}), 400
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT stock FROM inventory WHERE product_id = ?",
        (product_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return jsonify({"error":"Inventario no encontrado"}), 404
    
    stock_actual = row[0]

    if stock_actual < quantity:
        conn.close()
        return jsonify({
            "error": "Stock insuficiente",
            "stock_disponible": stock_actual,
            "quantity_solicitada": quantity
        }), 400

    nuevo_stock = stock_actual - quantity

    cursor.execute(
        "UPDATE inventory SET stock = ? WHERE product_id = ?",
        (nuevo_stock, product_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "product_id": product_id,
        "stock_anterior": stock_actual,
        "quantity_reservada": quantity,
        "stock_actual": nuevo_stock
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "inventory-service ok"}), 200