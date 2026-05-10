# ============================================================
# Module 12 — User Profile & Settings API
# ============================================================
# Endpoints:
#   GET    /profile/<user_id>          - View profile
#   PUT    /profile/update/<user_id>   - Update profile fields
#   POST   /profile/upload-photo       - Upload / set profile photo
#   DELETE /profile/delete/<user_id>   - Delete account
#   POST   /profile/save-destination   - Save a favourite city
# ============================================================

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, SavedDestination

profile_bp = Blueprint('profile', __name__)


# ----------------------------------------------------------
# GET /profile/<user_id> - View full profile
# ----------------------------------------------------------
@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Return a user's profile including saved destinations."""
    try:
        user = db.get_or_404(User, user_id)
        destinations = SavedDestination.query.filter_by(user_id=user_id).all()

        return jsonify({
            "id":                 user.id,
            "username":           user.username,
            "email":              user.email,
            "language":           user.language,
            "profile_photo":      user.profile_photo,
            "saved_destinations": [d.city_name for d in destinations]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# PUT /profile/update/<user_id> - Update profile fields
# ----------------------------------------------------------
@profile_bp.route('/update/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    """
    Update any combination of username, email, password, language.

    Example JSON body:
        {
            "username": "new_name",
            "email": "new@email.com",
            "language": "es"
        }
    """
    data = request.get_json()

    try:
        user = db.get_or_404(User, user_id)

        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        if 'language' in data:
            user.language = data['language']

        db.session.commit()

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# POST /profile/upload-photo - Set / update profile photo
# ----------------------------------------------------------
@profile_bp.route('/upload-photo', methods=['POST'])
def upload_photo():
    """
    Accept a photo URL or path and save it to the user's profile.
    For a hackathon demo this avoids multipart file handling.

    Expected JSON body:
        {
            "user_id": 1,
            "photo_url": "https://example.com/photo.jpg"
        }
    """
    data = request.get_json()

    if not data or 'user_id' not in data or 'photo_url' not in data:
        return jsonify({"error": "user_id and photo_url are required"}), 400

    try:
        user = db.get_or_404(User, data['user_id'])
        user.profile_photo = data['photo_url']
        db.session.commit()

        return jsonify({
            "message":   "Profile photo updated successfully",
            "photo_url": user.profile_photo
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# DELETE /profile/delete/<user_id> - Delete the account
# ----------------------------------------------------------
@profile_bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_profile(user_id):
    """
    Permanently delete a user account.
    Cascade rules in models.py will also remove the user's
    saved destinations, trips, packing items, and notes.
    """
    try:
        user = db.get_or_404(User, user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# POST /profile/save-destination - Save a favourite city
# ----------------------------------------------------------
@profile_bp.route('/save-destination', methods=['POST'])
def save_destination():
    """
    Add a city to the user's saved/favourite destinations.

    Expected JSON body:
        {
            "user_id": 1,
            "city_name": "London, UK"
        }
    """
    data = request.get_json()

    if not data or 'user_id' not in data or 'city_name' not in data:
        return jsonify({"error": "user_id and city_name are required"}), 400

    try:
        dest = SavedDestination(
            user_id   = data['user_id'],
            city_name = data['city_name']
        )
        db.session.add(dest)
        db.session.commit()

        return jsonify({
            "message": "Destination saved successfully",
            "id":      dest.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
