from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        fullname = data.get('fullname')
        email    = data.get('email')
        password = data.get('password')

        if not fullname or not email or not password:
            return jsonify({"success": False, "message": "All fields required.", "data": []}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already registered.", "data": []}), 400

        user = User(
            username=fullname,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"success": True, "message": "Account created!", "data": []}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email    = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password required.", "data": []}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"success": False, "message": "Invalid credentials.", "data": []}), 401

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "data": {
                "token": str(user.id),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.username
                }
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"success": True, "message": "Logged out.", "data": []}), 200