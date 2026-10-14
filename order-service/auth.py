import requests
import os

from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")

def validar_token(auth_header):
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL} /validate",
            headers={
                "Authorization": auth_header
            },
            timeout=5
        )

        return response

    except requests.RequestException:
        return None

def authorize(required_roles=None):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, (
            jsonify({"error": "Falta header Authorization"}),
            401
        )

    auth_response = validar_token(auth_header)

    if auth_response is None:
        return None, (
            jsonify({"error": "auth-service no está disponible"}),
            503
        )

    if auth_response.status_code != 200:
        return None, (
            jsonify(auth_response.json()),
            auth_response.status_code
        )

    auth_data = auth_response.json()
    role = auth_data["role"]

    if required_roles and role not in required_roles:
        return None, (
            jsonify({"error": "No tenés permisos para realizar esta acción"}),
            403
        )

    return auth_data, None