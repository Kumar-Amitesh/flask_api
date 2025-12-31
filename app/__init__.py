from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from flask_jwt_extended import JWTManager,jwt_required

# Loads variables from .env
load_dotenv()

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True
)

# Configuration for JWT
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers'] 
app.config['JWT_COOKIE_SECURE'] = False  #Set to True in production (requires HTTPS)
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'  # Defines the path for which the cookie is valid.
app.config['JWT_COOKIE_CSRF_PROTECT'] = True 

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

from app.config import db_config
db_config.init_db()

from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Root endpoint
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to Flask App",
    })