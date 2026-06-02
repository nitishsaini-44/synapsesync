import jwt
import datetime
import bcrypt
from flask import Blueprint, request, jsonify, current_app
from backend.database.db import create_user, get_user_by_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    name = data['name']
    email = data['email']
    password = data['password']

    # Hash the password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    # Create the user in the database
    new_user = create_user(name, email, password_hash)
    
    if not new_user:
        return jsonify({"error": "User with this email already exists"}), 409

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user['id'],
            "name": new_user['name'],
            "email": new_user['email']
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    email = data['email']
    password = data['password']

    # Retrieve user by email
    user = get_user_by_email(email)
    
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email']
        }
    }), 200
