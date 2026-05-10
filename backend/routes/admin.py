# ============================================================
# Module 14 — Admin Analytics Dashboard API
# ============================================================

from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db, User, Trip, TripNote, SavedDestination

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Return aggregate counts: users, trips, notes."""
    try:
        total_users = db.session.query(func.count(User.id)).scalar()
        total_trips = db.session.query(func.count(Trip.id)).scalar()
        total_notes = db.session.query(func.count(TripNote.id)).scalar()
        return jsonify({
            "total_users": total_users,
            "total_trips": total_trips,
            "total_notes": total_notes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/popular-cities', methods=['GET'])
def popular_cities():
    """Top 5 most-saved destinations using GROUP BY + ORDER BY."""
    try:
        saves_count = func.count(SavedDestination.id).label('saves')
        results = db.session.query(
            SavedDestination.city_name,
            saves_count
        ).group_by(SavedDestination.city_name) \
         .order_by(saves_count.desc()).limit(5).all()
        cities = [{"city": r[0], "saves": r[1]} for r in results]
        return jsonify({"popular_cities": cities}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/recent-users', methods=['GET'])
def recent_users():
    """5 most recently created users."""
    try:
        users = User.query.order_by(User.id.desc()).limit(5).all()
        users_list = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
        return jsonify({"recent_users": users_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/recent-trips', methods=['GET'])
def recent_trips():
    """5 most recently created trips."""
    try:
        trips = Trip.query.order_by(Trip.id.desc()).limit(5).all()
        trips_list = [{"id": t.id, "destination": t.destination, "user_id": t.user_id} for t in trips]
        return jsonify({"recent_trips": trips_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
