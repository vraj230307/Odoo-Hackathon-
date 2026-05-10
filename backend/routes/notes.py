# ============================================================
# Module 13 — Trip Notes / Journal API
# ============================================================

from flask import Blueprint, request, jsonify
from models import db, TripNote

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/add', methods=['POST'])
def add_note():
    """Add a note to a trip."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    for field in ['trip_id', 'note_title', 'note_content']:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    try:
        note = TripNote(
            trip_id=data['trip_id'],
            note_title=data['note_title'],
            note_content=data['note_content']
        )
        db.session.add(note)
        db.session.commit()
        return jsonify({
            "message": "Note added successfully",
            "note": {
                "id": note.id,
                "title": note.note_title,
                "content": note.note_content,
                "created_at": note.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@notes_bp.route('/<int:trip_id>', methods=['GET'])
def get_notes(trip_id):
    """Return every note for the given trip, newest first."""
    try:
        notes = TripNote.query.filter_by(trip_id=trip_id) \
            .order_by(TripNote.created_at.desc()).all()
        notes_list = [{
            "id": n.id,
            "title": n.note_title,
            "content": n.note_content,
            "created_at": n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for n in notes]
        return jsonify({"trip_id": trip_id, "total_notes": len(notes_list), "notes": notes_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notes_bp.route('/update/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update note title and/or content."""
    data = request.get_json()
    try:
        note = db.get_or_404(TripNote, note_id)
        if 'note_title' in data:
            note.note_title = data['note_title']
        if 'note_content' in data:
            note.note_content = data['note_content']
        db.session.commit()
        return jsonify({"message": "Note updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@notes_bp.route('/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a single note by its ID."""
    try:
        note = db.get_or_404(TripNote, note_id)
        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@notes_bp.route('/search', methods=['GET'])
def search_notes():
    """Search notes by keyword. Params: q (required), trip_id (optional)."""
    keyword = request.args.get('q', '')
    trip_id = request.args.get('trip_id')
    if not keyword:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    try:
        query = TripNote.query
        if trip_id:
            query = query.filter_by(trip_id=int(trip_id))
        query = query.filter(
            (TripNote.note_title.ilike(f'%{keyword}%')) |
            (TripNote.note_content.ilike(f'%{keyword}%'))
        )
        results = query.all()
        results_list = [{
            "id": n.id, "trip_id": n.trip_id,
            "title": n.note_title, "content": n.note_content
        } for n in results]
        return jsonify({"query": keyword, "results": results_list, "count": len(results_list)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
