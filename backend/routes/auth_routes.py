from flask import Blueprint, request, jsonify
from supabase_client import supabase

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        fullname = data.get('fullname')
        email    = data.get('email')
        password = data.get('password')

        if not fullname or not email or not password:
            return jsonify({ "success": False, "message": "All fields are required.", "data": [] }), 400

        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": { "data": { "full_name": fullname } }
        })

        if res.user:
            supabase.table("users_profile").insert({
                "id": res.user.id,
                "full_name": fullname,
                "email": email
            }).execute()

            return jsonify({ "success": True, "message": "Account created!", "data": [] }), 201
        else:
            return jsonify({ "success": False, "message": "Signup failed.", "data": [] }), 400

    except Exception as e:
        return jsonify({ "success": False, "message": str(e), "data": [] }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email    = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({ "success": False, "message": "Email and password required.", "data": [] }), 400

        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user:
            return jsonify({
                "success": True,
                "message": "Login successful.",
                "data": {
                    "token": res.session.access_token,
                    "user": {
                        "id": res.user.id,
                        "email": res.user.email,
                        "full_name": res.user.user_metadata.get("full_name", "")
                    }
                }
            }), 200
        else:
            return jsonify({ "success": False, "message": "Invalid credentials.", "data": [] }), 401

    except Exception as e:
        return jsonify({ "success": False, "message": str(e), "data": [] }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        supabase.auth.sign_out()
        return jsonify({ "success": True, "message": "Logged out.", "data": [] }), 200
    except Exception as e:
        return jsonify({ "success": False, "message": str(e), "data": [] }), 500