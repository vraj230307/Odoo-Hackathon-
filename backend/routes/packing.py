# ============================================================
# Module 10 — Packing Checklist API
# ============================================================
# Endpoints:
#   POST   /packing/add              - Add a packing item
#   GET    /packing/<trip_id>         - Get all items for a trip
#   PUT    /packing/update/<item_id>  - Update an item
#   DELETE /packing/delete/<item_id>  - Delete an item
#   POST   /packing/reset/<trip_id>   - Reset all items to unpacked
# ============================================================

from flask import Blueprint, request, jsonify
from models import db, PackingItem

# Create a Blueprint so this module stays self-contained
packing_bp = Blueprint('packing', __name__)


# ----------------------------------------------------------
# POST /packing/add - Add a new packing item
# ----------------------------------------------------------
@packing_bp.route('/add', methods=['POST'])
def add_item():
    """
    Add a new item to a trip's packing checklist.

    Expected JSON body:
        {
            "user_id": 1,
            "trip_id": 1,
            "item_name": "Sunscreen",
            "category": "Toiletries"     (optional, defaults to "General")
        }
    """
    data = request.get_json()

    # --- Validation ---
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ['user_id', 'trip_id', 'item_name']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        new_item = PackingItem(
            user_id   = data['user_id'],
            trip_id   = data['trip_id'],
            item_name = data['item_name'],
            category  = data.get('category', 'General')
        )
        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            "message": "Item added successfully",
            "item": {
                "id":            new_item.id,
                "item_name":     new_item.item_name,
                "category":      new_item.category,
                "packed_status": new_item.packed_status
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# GET /packing/<trip_id> - Get all items for a trip
# ----------------------------------------------------------
@packing_bp.route('/<int:trip_id>', methods=['GET'])
def get_items(trip_id):
    """Return every packing item that belongs to the given trip."""
    try:
        items = PackingItem.query.filter_by(trip_id=trip_id).all()

        items_list = [{
            "id":            item.id,
            "item_name":     item.item_name,
            "category":      item.category,
            "packed_status": item.packed_status,
            "created_at":    item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for item in items]

        return jsonify({
            "trip_id":     trip_id,
            "total_items": len(items_list),
            "items":       items_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# PUT /packing/update/<item_id> - Update item name, category, or status
# ----------------------------------------------------------
@packing_bp.route('/update/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update a packing item's fields.

    Any of these fields can be sent:
        {
            "item_name": "New Name",
            "category": "Electronics",
            "packed_status": true
        }
    """
    data = request.get_json()

    try:
        item = db.get_or_404(PackingItem, item_id)

        # Only update fields that are present in the request
        if 'item_name' in data:
            item.item_name = data['item_name']
        if 'category' in data:
            item.category = data['category']
        if 'packed_status' in data:
            item.packed_status = data['packed_status']

        db.session.commit()

        return jsonify({
            "message": "Item updated successfully",
            "item": {
                "id":            item.id,
                "item_name":     item.item_name,
                "category":      item.category,
                "packed_status": item.packed_status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# DELETE /packing/delete/<item_id> - Remove a packing item
# ----------------------------------------------------------
@packing_bp.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete a single packing item by its ID."""
    try:
        item = db.get_or_404(PackingItem, item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# POST /packing/reset/<trip_id> - Unpack everything
# ----------------------------------------------------------
@packing_bp.route('/reset/<int:trip_id>', methods=['POST'])
def reset_checklist(trip_id):
    """Set packed_status to False for every item in the given trip."""
    try:
        items = PackingItem.query.filter_by(trip_id=trip_id).all()

        if not items:
            return jsonify({"message": "No items found for this trip"}), 404

        for item in items:
            item.packed_status = False

        db.session.commit()

        return jsonify({
            "message": f"Checklist for trip {trip_id} has been reset",
            "items_reset": len(items)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
