from flask import Blueprint, request, jsonify

from auth import authorize

from repository import (
    get_all_products,
    get_product_by_id_db,
    create_product_db,
    update_product_db,
    delete_product_db
)

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods=["GET"])
def get_products():

    auth_data, error = authorize(["admin", "service"])

    if error:
        return error

    rows = get_all_products()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1]
        })

    return jsonify(products), 200

@products_bp.route("/products/<int:id>", methods=["GET"])
def get_product_by_id(id):

    auth_data, error = authorize(["admin", "service"])

    if error:
        return error

    row = get_product_by_id_db(id)

    if row is None:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "id": row[0],
        "name": row[1]
    }), 200

@products_bp.route("/products", methods=["POST"])
def create_product():

    auth_data, error = authorize(["admin"])

    if error:
        return error

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Falta el campo name"}), 400

    new_id = create_product_db(data["name"])

    return jsonify({
        "id": new_id,
        "name": data["name"]
    }), 201

@products_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):

    auth_data, error = authorize(["admin"])
    
    if error:
        return error

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Falta el campo name"}), 400

    updated = update_product_db(id, data["name"])

    if updated == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({
        "id": id,
        "name": data["name"]
    }), 200

@products_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    auth_data, error = authorize(["admin"])
    
    if error:
        return error

    deleted = delete_product_db(id)

    if deleted == 0:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify({"message":"Producto eliminado"}), 200

@products_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "product-service ok"}), 200


