# backend/routes/city_routes.py
# Traveloop — Member 3: City API Routes
# All responses follow: {"success": true, "message": "...", "data": [...]}

from flask import Blueprint, request, jsonify
from extensions import db          # SQLAlchemy instance from extensions.py
from models.city import City       # City SQLAlchemy model
from sqlalchemy import or_, func

city_bp = Blueprint("city_bp", __name__, url_prefix="/cities")


# ── Helpers ────────────────────────────────────────────────────────────────

def success(data, message="OK", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def failure(message, status=400):
    return jsonify({"success": False, "message": message, "data": []}), status


def city_to_dict(c: City) -> dict:
    """Serialise a City ORM object to a plain dict."""
    return {
        "id":               str(c.id),
        "name":             c.name,
        "country":          c.country,
        "region":           c.region,
        "emoji":            c.emoji or "🏙️",
        "avg_cost_per_day": float(c.avg_cost_per_day or 0),
        "rating":           float(c.rating or 0),
        "featured":         bool(c.featured),
        "description":      c.description or "",
        "image_url":        c.image_url or "",
        "lat":              float(c.lat or 0),
        "lng":              float(c.lng or 0),
    }


# ── GET /cities ─────────────────────────────────────────────────────────────

@city_bp.route("", methods=["GET"])
def get_cities():
    """
    Retrieve cities with optional search, filter, and sort.

    Query params:
        q        (str)   — full-text search on name / country
        country  (str)   — exact country filter
        region   (str)   — exact region filter
        sort     (str)   — name | cost_asc | cost_desc | rating  (default: name)
        limit    (int)   — max results (default 200, max 500)
        offset   (int)   — pagination offset (default 0)
    """
    q       = request.args.get("q", "").strip()
    country = request.args.get("country", "").strip()
    region  = request.args.get("region", "").strip()
    sort    = request.args.get("sort", "name").strip().lower()
    limit   = min(int(request.args.get("limit",  200)), 500)
    offset  = max(int(request.args.get("offset",   0)),   0)

    query = City.query

    # Full-text search
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                City.name.ilike(like),
                City.country.ilike(like),
                City.region.ilike(like),
            )
        )

    # Filters
    if country:
        query = query.filter(func.lower(City.country) == country.lower())
    if region:
        query = query.filter(func.lower(City.region) == region.lower())

    # Sorting
    sort_map = {
        "name":      City.name.asc(),
        "cost_asc":  City.avg_cost_per_day.asc(),
        "cost_desc": City.avg_cost_per_day.desc(),
        "rating":    City.rating.desc(),
    }
    query = query.order_by(sort_map.get(sort, City.name.asc()))

    # Pagination
    cities = query.offset(offset).limit(limit).all()

    # Deduplicate by id (safety net at API level)
    seen, unique = set(), []
    for c in cities:
        if c.id not in seen:
            seen.add(c.id)
            unique.append(city_to_dict(c))

    return success(unique, f"Returned {len(unique)} cities")


# ── GET /cities/<id> ─────────────────────────────────────────────────────────

@city_bp.route("/<int:city_id>", methods=["GET"])
def get_city(city_id):
    """Return a single city by primary key."""
    city = City.query.get(city_id)
    if not city:
        return failure("City not found", 404)
    return success(city_to_dict(city), "City found")


# ── GET /cities/regions ──────────────────────────────────────────────────────

@city_bp.route("/regions", methods=["GET"])
def get_regions():
    """Return distinct regions with city counts."""
    rows = (
        db.session.query(City.region, func.count(City.id).label("count"))
        .filter(City.region.isnot(None))
        .group_by(City.region)
        .order_by(City.region.asc())
        .all()
    )
    data = [{"region": r, "count": c} for r, c in rows]
    return success(data, f"Returned {len(data)} regions")


# ── GET /cities/countries ────────────────────────────────────────────────────

@city_bp.route("/countries", methods=["GET"])
def get_countries():
    """Return distinct countries (optionally filtered by region)."""
    region = request.args.get("region", "").strip()
    query  = db.session.query(City.country, func.count(City.id).label("count")).filter(City.country.isnot(None))
    if region:
        query = query.filter(func.lower(City.region) == region.lower())
    rows = query.group_by(City.country).order_by(City.country.asc()).all()
    data = [{"country": c, "count": n} for c, n in rows]
    return success(data, f"Returned {len(data)} countries")
