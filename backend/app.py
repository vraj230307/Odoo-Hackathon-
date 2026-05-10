# ============================================================
# Traveloop — Main Application Entry Point
# ============================================================

from flask import Flask, jsonify, render_template
from config import Config
from models import db

# Import Blueprints from each module
from routes.packing import packing_bp
from routes.itinerary import itinerary_bp
from routes.profile import profile_bp
from routes.notes import notes_bp
from routes.admin import admin_bp


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Register each module as a Blueprint with its URL prefix
    app.register_blueprint(packing_bp,   url_prefix='/packing')
    app.register_blueprint(itinerary_bp, url_prefix='/share')
    app.register_blueprint(profile_bp,   url_prefix='/profile')
    app.register_blueprint(notes_bp,     url_prefix='/notes')
    app.register_blueprint(admin_bp,     url_prefix='/admin')

    # ---- UI Routes ----
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/ui/packing')
    def ui_packing():
        return render_template('packing.html')

    @app.route('/ui/profile')
    def ui_profile():
        return render_template('profile.html')

    @app.route('/ui/notes')
    def ui_notes():
        return render_template('notes.html')

    @app.route('/ui/admin')
    def ui_admin():
        return render_template('admin.html')

    @app.route('/ui/share/<token>')
    def ui_share(token):
        # We pass the token to the template so it can fetch the correct data
        return render_template('shared.html', token=token)

    # ---- Global error handlers ----
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return app


# ---- Run the app ----
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()          # Create all tables if they don't exist
    app.run(debug=True, port=5000)
