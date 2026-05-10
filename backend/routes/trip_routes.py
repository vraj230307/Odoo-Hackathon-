from flask import Blueprint, request, jsonify
from models import db, Trip

trip_routes = Blueprint('trip_routes', __name__)

@trip_routes.route('/trips', methods=['GET'])
def get_trips():
    try:
        trips = Trip.query.all()
        data = [{"id": t.id, "destination": t.destination, "created_at": str(t.created_at)} for t in trips]
        return jsonify({"success": True, "message": "Fetched all trips successfully", "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500

@trip_routes.route('/trip', methods=['POST'])
def create_trip():
    try:
        data        = request.get_json()
        user_id     = data.get('user_id', 1)
        destination = data.get('destination') or data.get('name', 'Unknown')
        trip = Trip(user_id=user_id, destination=destination)
        db.session.add(trip)
        db.session.commit()
        return jsonify({"success": True, "message": "Trip created successfully", "data": {"id": trip.id}}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500

@trip_routes.route('/trip/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    try:
        trip = Trip.query.get(trip_id)
        if not trip:
            return jsonify({"success": False, "message": "Trip not found", "data": []}), 404
        return jsonify({"success": True, "message": "Fetched", "data": {"id": trip.id, "destination": trip.destination}}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500

@trip_routes.route('/trip/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    try:
        trip = Trip.query.get(trip_id)
        if trip:
            db.session.delete(trip)
            db.session.commit()
        return jsonify({"success": True, "message": "Deleted", "data": []}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500