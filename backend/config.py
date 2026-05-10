import os

# ============================================================
# Configuration for the Traveloop Flask Application
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration class."""

    # Secret key used for sessions, token generation, etc.
    SECRET_KEY = 'traveloop-hackathon-secret-key-2026'

    # SQLite database file stored in the project root
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')

    # Disable the Flask-SQLAlchemy event system to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder for profile photos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
