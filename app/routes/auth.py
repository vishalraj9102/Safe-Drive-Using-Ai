from flask import Blueprint, request, session, jsonify
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")  # 👈 missing part
    password = data.get("password")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    session['user'] = user.email
    return jsonify({"message": "Login successful"}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user_id = data.get("user_id")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check if logged in user matches session user
    if session.get('user') != user.email:
        return jsonify({"message": "Unauthorized logout attempt"}), 403

    session.pop('user', None)
    return jsonify({"message": "Logged out successfully"}), 200
