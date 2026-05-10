# backend/routes/city_routes.py

from flask import Blueprint, jsonify, request
from database import get_db_connection

city_routes = Blueprint('city_routes', **name**)

# =========================

# GET ALL CITIES

# =========================

@city_routes.route('/cities', methods=['GET'])
def get_cities():

```
country = request.args.get('country')
region = request.args.get('region')
search = request.args.get('search')

conn = get_db_connection()
cursor = conn.cursor()

query = "SELECT * FROM cities WHERE 1=1"
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

return jsonify({
    "success": True,
    "message": "Cities fetched successfully",
    "data": cities
})
```

# =========================

# GET ACTIVITIES

# =========================

@city_routes.route('/activities', methods=['GET'])
def get_activities():

```
category = request.args.get('category')
max_cost = request.args.get('max_cost')
search = request.args.get('search')

conn = get_db_connection()
cursor = conn.cursor()

query = """
    SELECT
        activities.id,
        activities.name,
        activities.category,
        activities.cost,
        cities.name as city
    FROM activities
    JOIN cities
    ON activities.city_id = cities.id
    WHERE 1=1
"""

params = []

if category:
    query += " AND activities.category = ?"
    params.append(category)

if max_cost:
    query += " AND activities.cost <= ?"
    params.append(max_cost)

if search:
    query += " AND activities.name LIKE ?"
    params.append(f"%{search}%")

cursor.execute(query, params)

activities = [dict(row) for row in cursor.fetchall()]

conn.close()

return jsonify({
    "success": True,
    "message": "Activities fetched successfully",
    "data": activities
})
```
