# ============================================================
# Module 11 — Shared / Public Itinerary API
# ============================================================

from flask import Blueprint, request, jsonify
from models import db, SharedItinerary, Trip, PackingItem, TripNote
from utils.helpers import generate_public_token

itinerary_bp = Blueprint('itinerary', __name__)


@itinerary_bp.route('/create/<int:trip_id>', methods=['POST'])
def create_shared_itinerary(trip_id):
    """Generate a unique public token for a trip."""
    try:
        trip = db.get_or_404(Trip, trip_id)

        existing = SharedItinerary.query.filter_by(trip_id=trip_id).first()
        if existing:
            return jsonify({
                "message": "Trip already has a public link",
                "token":   existing.public_token,
                "link":    f"/share/{existing.public_token}"
            }), 200

        token = generate_public_token()
        new_share = SharedItinerary(trip_id=trip_id, public_token=token)
        db.session.add(new_share)
        db.session.commit()

        return jsonify({
            "message": "Public link generated successfully",
            "token":   token,
            "link":    f"/share/{token}"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@itinerary_bp.route('/<string:token>', methods=['GET'])
def get_shared_itinerary(token):
    """Public read-only access to a trip using its share token."""
    try:
        share = SharedItinerary.query.filter_by(public_token=token).first()
        if not share:
            return jsonify({"error": "Invalid or expired share link"}), 404

        trip = db.session.get(Trip, share.trip_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404

        packing = PackingItem.query.filter_by(trip_id=trip.id).all()
        packing_list = [{
            "item_name": p.item_name,
            "category": p.category,
            "packed_status": p.packed_status
        } for p in packing]

        notes = TripNote.query.filter_by(trip_id=trip.id).all()
        notes_list = [{
            "title": n.note_title,
            "content": n.note_content
        } for n in notes]

        return jsonify({
            "message": "Shared itinerary fetched successfully",
            "trip": {
                "id": trip.id,
                "destination": trip.destination,
                "created_at": trip.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            "packing_items": packing_list,
            "notes": notes_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@itinerary_bp.route('/copy/<string:token>', methods=['POST'])
def copy_itinerary(token):
    """Copy a shared itinerary into the requesting user's account."""
    data = request.get_json()

    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400

    user_id = data['user_id']

    try:
        share = SharedItinerary.query.filter_by(public_token=token).first()
        if not share:
            return jsonify({"error": "Invalid or expired share link"}), 404

        original_trip = db.session.get(Trip, share.trip_id)
        if not original_trip:
            return jsonify({"error": "Original trip not found"}), 404

        new_trip = Trip(user_id=user_id, destination=original_trip.destination)
        db.session.add(new_trip)
        db.session.flush()

        original_items = PackingItem.query.filter_by(trip_id=original_trip.id).all()
        for item in original_items:
            clone = PackingItem(
                user_id=user_id, trip_id=new_trip.id,
                item_name=item.item_name, category=item.category
            )
            db.session.add(clone)

        original_notes = TripNote.query.filter_by(trip_id=original_trip.id).all()
        for note in original_notes:
            clone = TripNote(
                trip_id=new_trip.id,
                note_title=note.note_title,
                note_content=note.note_content
            )
            db.session.add(clone)

        db.session.commit()

        return jsonify({
            "message": "Itinerary copied successfully",
            "new_trip_id": new_trip.id,
            "items_copied": len(original_items),
            "notes_copied": len(original_notes)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
