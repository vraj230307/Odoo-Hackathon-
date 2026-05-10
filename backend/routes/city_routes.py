from flask import Blueprint, jsonify, request
from models import db
import sqlite3
import os

city_bp = Blueprint('city', __name__)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@city_bp.route('/cities', methods=['GET'])
def get_cities():
    try:
        country = request.args.get('country')
        region  = request.args.get('region')
        search  = request.args.get('search')

        conn   = get_db()
        cursor = conn.cursor()

        query  = "SELECT * FROM cities WHERE 1=1"
        params = []

        if country:
            query += " AND country = ?"
            params.append(country)
        if region:
            query += " AND region = ?"
            params.append(region)
        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")

        cursor.execute(query, params)
        cities = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({"success": True, "message": "Cities fetched.", "data": cities}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500


@city_bp.route('/activities', methods=['GET'])
def get_activities():
    try:
        category = request.args.get('category')
        max_cost = request.args.get('max_cost')
        search   = request.args.get('search')

        conn   = get_db()
        cursor = conn.cursor()

        query = """
            SELECT a.id, a.name, a.category, a.cost, c.name as city
            FROM activities a
            JOIN cities c ON a.city_id = c.id
            WHERE 1=1
        """
        params = []

        if category:
            query += " AND a.category = ?"
            params.append(category)
        if max_cost:
            query += " AND a.cost <= ?"
            params.append(float(max_cost))
        if search:
            query += " AND a.name LIKE ?"
            params.append(f"%{search}%")

        cursor.execute(query, params)
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({"success": True, "message": "Activities fetched.", "data": activities}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": []}), 500