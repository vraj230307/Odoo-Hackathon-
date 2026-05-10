from flask import Blueprint, request, jsonify

itinerary_routes = Blueprint('itinerary_routes', __name__)

@itinerary_routes.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    return jsonify({
        "success": True,
        "message": f"Fetched itinerary for trip {trip_id}",
        "data": []
    }), 200

@itinerary_routes.route('/itinerary/<trip_id>/stops', methods=['POST'])
def add_itinerary_stop(trip_id):
    return jsonify({
        "success": True,
        "message": "Itinerary stop added",
        "data": []
    }), 201

