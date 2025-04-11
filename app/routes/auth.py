from flask import Blueprint, request, jsonify
from app.models.user import User, Contact
from app import db, redis_client
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        fullname = data.get("fullname")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not all([fullname, email, password, confirm_password]):
            return jsonify({"message": "All fields are required"}), 400

        if password != confirm_password:
            return jsonify({"message": "Passwords do not match"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=fullname, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        redis_client.hset(f"user:{email}", mapping={
            "username": fullname,
            "email": email,
            "password": hashed_password
        })
        redis_client.expire(f"user:{email}", 300)

        return jsonify({"message": "Registered successfully"}), 201

    except Exception as e:
        return jsonify({"message": f"Signup failed: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        cached_user = redis_client.hgetall(f"user:{email}")
        if cached_user:
            if not check_password_hash(cached_user['password'], password):
                return jsonify({"message": "Invalid credentials"}), 401

            token = create_access_token(identity=email)
            return jsonify({"message": "Login successful (from cache)", "token": token}), 200

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        redis_client.hset(f"user:{email}", mapping={
            "username": user.username,
            "email": user.email,
            "password": user.password
        })
        redis_client.expire(f"user:{email}", 300)

        token = create_access_token(identity=email)
        return jsonify({"message": "Login successful", "token": token}), 200

    except Exception as e:
        return jsonify({"message": f"Login failed: {str(e)}"}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user_email = get_jwt_identity()
        cached_user = redis_client.hgetall(f"user:{current_user_email}")

        if cached_user:
            return jsonify({
                "username": cached_user.get("username"),
                "email": cached_user.get("email")
            }), 200

        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        redis_client.hset(f"user:{user.email}", mapping={
            "username": user.username,
            "email": user.email,
            "password": user.password
        })
        redis_client.expire(f"user:{user.email}", 300)

        return jsonify({
            "username": user.username,
            "email": user.email
        }), 200

    except Exception as e:
        return jsonify({"message": f"Profile error: {str(e)}"}), 500


@auth_bp.route('/contact', methods=['POST'])
def contact_us():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({"message": "All fields are required"}), 400

        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        redis_client.hset(f"contact:{email}", mapping={
            "name": name,
            "email": email,
            "message": message
        })
        redis_client.expire(f"contact:{email}", 600)

        return jsonify({"message": "Thanks for contacting us!"}), 201

    except Exception as e:
        return jsonify({"message": f"Contact failed: {str(e)}"}), 500
