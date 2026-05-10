# ============================================================
# Database Models for Traveloop
# ============================================================
# This file defines every table used by Modules 10-14.
# Each class maps to a SQLite table via SQLAlchemy ORM.
# ============================================================

from datetime import datetime, timezone
from typing import Optional
from flask_sqlalchemy import SQLAlchemy

# Create the single SQLAlchemy instance shared across the app
db = SQLAlchemy()


# ----------------------------------------------------------
# User model (Module 12 — Profile & Settings)
# ----------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password      = db.Column(db.String(200), nullable=False)   # hashed
    profile_photo = db.Column(db.String(255), nullable=True)    # file path or URL
    language      = db.Column(db.String(20), default='en')

    # Relationships
    destinations = db.relationship('SavedDestination', backref='user',
                                   lazy=True, cascade='all, delete-orphan')
    trips        = db.relationship('Trip', backref='user',
                                   lazy=True, cascade='all, delete-orphan')

    def __init__(self, username: str, email: str, password: str,
                 profile_photo: Optional[str] = None,
                 language: str = 'en') -> None:
        self.username = username
        self.email = email
        self.password = password
        self.profile_photo = profile_photo
        self.language = language


# ----------------------------------------------------------
# Saved Destination model (Module 12)
# ----------------------------------------------------------
class SavedDestination(db.Model):
    __tablename__ = 'saved_destinations'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)

    def __init__(self, user_id: int, city_name: str) -> None:
        self.user_id = user_id
        self.city_name = city_name


# ----------------------------------------------------------
# Trip model (lightweight — used as FK target for other modules)
# ----------------------------------------------------------
class Trip(db.Model):
    __tablename__ = 'trips'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    packing_items = db.relationship('PackingItem', backref='trip',
                                    lazy=True, cascade='all, delete-orphan')
    notes         = db.relationship('TripNote', backref='trip',
                                    lazy=True, cascade='all, delete-orphan')
    shares        = db.relationship('SharedItinerary', backref='trip',
                                    lazy=True, cascade='all, delete-orphan')

    def __init__(self, user_id: int, destination: str) -> None:
        self.user_id = user_id
        self.destination = destination


# ----------------------------------------------------------
# Packing Item model (Module 10 — Packing Checklist)
# ----------------------------------------------------------
class PackingItem(db.Model):
    __tablename__ = 'packing_items'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id       = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    item_name     = db.Column(db.String(100), nullable=False)
    category      = db.Column(db.String(50), default='General')
    packed_status = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, user_id: int, trip_id: int, item_name: str,
                 category: str = 'General', packed_status: bool = False) -> None:
        self.user_id = user_id
        self.trip_id = trip_id
        self.item_name = item_name
        self.category = category
        self.packed_status = packed_status


# ----------------------------------------------------------
# Shared Itinerary model (Module 11 — Public Itinerary)
# ----------------------------------------------------------
class SharedItinerary(db.Model):
    __tablename__ = 'shared_itineraries'

    id           = db.Column(db.Integer, primary_key=True)
    trip_id      = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    public_token = db.Column(db.String(64), unique=True, nullable=False)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, trip_id: int, public_token: str) -> None:
        self.trip_id = trip_id
        self.public_token = public_token


# ----------------------------------------------------------
# Trip Note model (Module 13 — Trip Notes / Journal)
# ----------------------------------------------------------
class TripNote(db.Model):
    __tablename__ = 'trip_notes'

    id           = db.Column(db.Integer, primary_key=True)
    trip_id      = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    note_title   = db.Column(db.String(150), nullable=False)
    note_content = db.Column(db.Text, nullable=False)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, trip_id: int, note_title: str, note_content: str) -> None:
        self.trip_id = trip_id
        self.note_title = note_title
        self.note_content = note_content
