# backend/routes/budget_routes.py

from flask import Blueprint, jsonify, request
from database import get_db_connection

budget_routes = Blueprint('budget_routes', **name**)

@budget_routes.route('/budget/calculate', methods=['POST'])
def calculate_budget():

```
data = request.get_json()

days = int(data.get('days', 1))
selected_activities = data.get('activities', [])

conn = get_db_connection()
cursor = conn.cursor()

total_activity_cost = 0

if selected_activities:

    placeholders = ",".join(["?"] * len(selected_activities))

    query = f"""
        SELECT SUM(cost) as total
        FROM activities
        WHERE id IN ({placeholders})
    """

    cursor.execute(query, selected_activities)

    result = cursor.fetchone()

    if result['total']:
        total_activity_cost = result['total']

conn.close()

hotel_cost = days * 3000
transport_cost = days * 1200

total_budget = (
    hotel_cost +
    transport_cost +
    total_activity_cost
)

average_per_day = round(total_budget / days, 2)

alert = ""

if total_budget > 50000:
    alert = "⚠️ High budget trip"
elif total_budget > 25000:
    alert = "Moderate budget trip"
else:
    alert = "Budget friendly trip"

return jsonify({
    "success": True,
    "message": "Budget calculated successfully",
    "data": {
        "total_budget": total_budget,
        "average_per_day": average_per_day,
        "hotel": hotel_cost,
        "transport": transport_cost,
        "activities": total_activity_cost,
        "alert": alert
    }
})
```
