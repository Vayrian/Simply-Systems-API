from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = generate_password_hash(password)
    user = User(email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    print(f"[REGISTER] New user {email}, ID {user.id}")

    return jsonify({
        "message": "Registered",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    print(f"[LOGIN] Success for {email}")

    return jsonify({
        "message": "Logged in",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name
        }
    }), 200