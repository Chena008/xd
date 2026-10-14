from flask import Flask, jsonify
from repository import init_db

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "order-service ok"}), 200

if __name__ == "__main__":
    init_db()               
    app.run(port=5002, debug=True)