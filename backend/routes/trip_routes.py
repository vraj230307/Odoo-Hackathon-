from flask import Blueprint, request, jsonify

trip_routes = Blueprint('trip_routes', __name__)

@trip_routes.route('/trips', methods=['GET'])
def get_trips():
    return jsonify({
        "success": True,
        "message": "Fetched all trips successfully",
        "data": []
    }), 200

@trip_routes.route('/trip', methods=['POST'])
def create_trip():
    return jsonify({
        "success": True,
        "message": "Trip created successfully",
        "data": []
    }), 201

@trip_routes.route('/trip/<trip_id>', methods=['GET'])
def get_trip(trip_id):
    return jsonify({
        "success": True,
        "message": f"Fetched trip {trip_id}",
        "data": []
    }), 200

@trip_routes.route('/trip/<trip_id>', methods=['PUT'])
def update_trip(trip_id):
    return jsonify({
        "success": True,
        "message": f"Updated trip {trip_id}",
        "data": []
    }), 200

@trip_routes.route('/trip/<trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    return jsonify({
        "success": True,
        "message": f"Deleted trip {trip_id}",
        "data": []
    }), 200
