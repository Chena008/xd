from flask import Flask
from repository import init_db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
PRODUCT_SERVICE_URL= os.getenv("PRODUCT_SERVICE_URL")

if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)