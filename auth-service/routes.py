from app import app
from flask import request, jsonify

TOKENS_VALIDOS = {
    "token_admin": "admin",
    "token_service": "service"
}

@app.route("/validate", methods=["POST"])
def validate_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Falta header Authorization"}), 401

    partes = auth_header.split(" ")

    if len(partes) != 2 or partes[0] != "Bearer":
        return jsonify({"error": "Formato inválido. Usá Bearer <token>"}), 401

    token = partes[1]

    if token not in TOKENS_VALIDOS:
        return jsonify({"error": "Token inválido"}), 403

    return jsonify({
        "valid": True,
        "role": TOKENS_VALIDOS[token]
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "auth-service ok"}), 200