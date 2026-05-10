# backend/routes/budget_routes.py
# Traveloop — Member 3: Budget API Routes
# All responses follow: {"success": true, "message": "...", "data": {...}}

from flask import Blueprint, request, jsonify
from extensions import db
from models.city import City
from models.activity import Activity
from models.expense import Expense
from sqlalchemy import func

budget_bp = Blueprint("budget_bp", __name__, url_prefix="/budget")


# ── Helpers ────────────────────────────────────────────────────────────────

def success(data, message="OK", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def failure(message, status=400):
    return jsonify({"success": False, "message": message, "data": {}}), status


# Cost multipliers by travel style (relative to mid-range base)
STYLE_MULTIPLIERS = {
    "budget":  0.55,
    "mid":     1.00,
    "luxury":  2.40,
}

# Category cost weights (fraction of total daily spend)
CATEGORY_WEIGHTS = {
    "accommodation": 0.35,
    "food":          0.25,
    "transport":     0.15,
    "activities":    0.15,
    "shopping":      0.07,
    "other":         0.03,
}

CURRENCY_RATES = {            # approximate rates vs INR
    "INR": 1.0,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0094,
    "JPY": 1.78,
}


def convert(amount_inr: float, currency: str) -> float:
    rate = CURRENCY_RATES.get(currency, 1.0)
    return round(amount_inr * rate, 2)


# ── POST /budget/calculate ───────────────────────────────────────────────────

@budget_bp.route("/calculate", methods=["POST"])
def calculate_budget():
    """
    Estimate total trip budget for a city.

    Request body (JSON):
        city      (str, required) — destination city name
        days      (int)           — trip duration in days (default 5)
        people    (int)           — number of travellers (default 1)
        style     (str)           — budget | mid | luxury (default mid)
        currency  (str)           — INR | USD | EUR | GBP | JPY (default INR)

    Returns estimated cost_per_day, total_cost, and category breakdown.
    """
    body = request.get_json(silent=True) or {}

    city_name = (body.get("city") or "").strip()
    days      = max(1, int(body.get("days", 5)))
    people    = max(1, int(body.get("people", 1)))
    style     = body.get("style", "mid").lower()
    currency  = body.get("currency", "INR").upper()

    if not city_name:
        return failure("Field 'city' is required.")
    if style not in STYLE_MULTIPLIERS:
        return failure(f"Invalid style '{style}'. Choose: budget, mid, luxury.")
    if currency not in CURRENCY_RATES:
        return failure(f"Unsupported currency '{currency}'.")

    # Look up city base cost from DB (INR per day for 1 person)
    city = City.query.filter(func.lower(City.name) == city_name.lower()).first()
    base_cost_per_day = float(city.avg_cost_per_day) if city else 3500.0   # sensible default

    multiplier   = STYLE_MULTIPLIERS[style]
    adjusted_cpd = base_cost_per_day * multiplier          # INR, per person per day
    total_inr    = adjusted_cpd * days * people

    # Category breakdown
    breakdown_inr = {
        "Accommodation": total_inr * CATEGORY_WEIGHTS["accommodation"],
        "Food":          total_inr * CATEGORY_WEIGHTS["food"],
        "Transport":     total_inr * CATEGORY_WEIGHTS["transport"],
        "Activities":    total_inr * CATEGORY_WEIGHTS["activities"],
        "Shopping":      total_inr * CATEGORY_WEIGHTS["shopping"],
        "Other":         total_inr * CATEGORY_WEIGHTS["other"],
    }

    # Convert to requested currency
    def c(v): return convert(v, currency)

    data = {
        "city":          city_name,
        "days":          days,
        "people":        people,
        "style":         style,
        "currency":      currency,
        "cost_per_day":  c(adjusted_cpd * people),
        "total_cost":    c(total_inr),
        "breakdown":     {k: c(v) for k, v in breakdown_inr.items()},
        "city_found":    city is not None,
    }
    return success(data, f"Budget estimate for {city_name}")


# ── GET /budget/summary ──────────────────────────────────────────────────────

@budget_bp.route("/summary", methods=["GET"])
def budget_summary():
    """
    Aggregate expense summary for a trip.

    Query params:
        trip_id  (str, required) — trip identifier
        currency (str)           — response currency (default INR)
    """
    trip_id  = request.args.get("trip_id", "").strip()
    currency = request.args.get("currency", "INR").upper()

    if not trip_id:
        return failure("Query param 'trip_id' is required.")

    expenses = Expense.query.filter_by(trip_id=trip_id).all()
    if not expenses:
        return success({
            "trip_id":       trip_id,
            "total_spent":   0,
            "by_category":   {},
            "daily_average": 0,
            "expense_count": 0,
        }, "No expenses found for this trip")

    total_inr   = sum(float(e.amount) for e in expenses)
    by_category = {}
    for exp in expenses:
        by_category[exp.category] = by_category.get(exp.category, 0) + float(exp.amount)

    # Unique dates for daily average
    unique_dates = len({e.date for e in expenses if e.date})
    daily_avg    = total_inr / max(unique_dates, 1)

    def c(v): return convert(v, currency)

    data = {
        "trip_id":        trip_id,
        "currency":       currency,
        "total_spent":    c(total_inr),
        "by_category":    {k: c(v) for k, v in by_category.items()},
        "daily_average":  c(daily_avg),
        "expense_count":  len(expenses),
        "unique_days":    unique_dates,
    }
    return success(data, "Budget summary retrieved")


# ── POST /budget/expenses ────────────────────────────────────────────────────

@budget_bp.route("/expenses", methods=["POST"])
def add_expense():
    """
    Persist a new expense entry to the DB.

    Request body (JSON):
        trip_id     (str, required)
        description (str, required)
        amount      (float, required)
        category    (str)  — default "Other"
        date        (str)  — ISO date YYYY-MM-DD, default today
    """
    body = request.get_json(silent=True) or {}

    trip_id     = (body.get("trip_id") or "").strip()
    description = (body.get("description") or "").strip()
    amount      = body.get("amount")
    category    = (body.get("category") or "Other").strip()
    date        = (body.get("date") or "").strip() or None

    if not trip_id:
        return failure("Field 'trip_id' is required.")
    if not description:
        return failure("Field 'description' is required.")
    try:
        amount = float(amount)
        if amount < 0:
            raise ValueError
    except (TypeError, ValueError):
        return failure("Field 'amount' must be a non-negative number.")

    expense = Expense(
        trip_id=trip_id,
        description=description,
        amount=amount,
        category=category,
        date=date,
    )
    db.session.add(expense)
    db.session.commit()

    data = {
        "id":          expense.id,
        "trip_id":     expense.trip_id,
        "description": expense.description,
        "amount":      float(expense.amount),
        "category":    expense.category,
        "date":        str(expense.date) if expense.date else None,
    }
    return success(data, "Expense added successfully", 201)


# ── DELETE /budget/expenses/<id> ─────────────────────────────────────────────

@budget_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    """Delete a single expense by id."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return failure("Expense not found", 404)
    db.session.delete(expense)
    db.session.commit()
    return success({"id": expense_id}, "Expense deleted")


# ── GET /budget/activities-cost ──────────────────────────────────────────────

@budget_bp.route("/activities-cost", methods=["GET"])
def activities_cost():
    """
    Return total estimated cost for a list of activity ids.

    Query param:
        ids  (str) — comma-separated activity ids, e.g. ?ids=1,3,7
    """
    ids_param = request.args.get("ids", "").strip()
    if not ids_param:
        return failure("Query param 'ids' (comma-separated) is required.")

    try:
        ids = [int(i.strip()) for i in ids_param.split(",") if i.strip()]
    except ValueError:
        return failure("'ids' must be comma-separated integers.")

    activities = Activity.query.filter(Activity.id.in_(ids)).all()
    found_ids  = {a.id for a in activities}
    total      = sum(float(a.cost or 0) for a in activities)

    data = {
        "requested_ids": ids,
        "found_ids":     list(found_ids),
        "missing_ids":   [i for i in ids if i not in found_ids],
        "total_cost":    total,
        "activities":    [
            {"id": a.id, "name": a.name, "cost": float(a.cost or 0), "category": a.category}
            for a in activities
        ],
    }
    return success(data, f"Cost calculated for {len(activities)} activities")
