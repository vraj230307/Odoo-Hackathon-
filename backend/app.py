from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db

# Module 4 routes
from routes.packing import packing_bp
from routes.itinerary import itinerary_bp
from routes.profile import profile_bp
from routes.notes import notes_bp
from routes.admin import admin_bp

# Module 1 routes (auth)
from routes.auth_routes import auth_bp

# Module 2 routes
from routes.trip_routes import trip_routes as trip_bp

# Module 3 routes
from routes.city_routes import city_bp
from routes.budget_routes import budget_bp

def create_app():
    app = Flask(__name__,
            template_folder='../frontend/pages',
            static_folder='../frontend',
            static_url_path='')
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    # Register all blueprints
    app.register_blueprint(auth_bp,      url_prefix='/api')
    app.register_blueprint(trip_bp,      url_prefix='/api')
    app.register_blueprint(city_bp,      url_prefix='/api')
    app.register_blueprint(budget_bp,    url_prefix='/api')
    app.register_blueprint(packing_bp,   url_prefix='/packing')
    app.register_blueprint(itinerary_bp, url_prefix='/share')
    app.register_blueprint(profile_bp,   url_prefix='/profile')
    app.register_blueprint(notes_bp,     url_prefix='/notes')
    app.register_blueprint(admin_bp,     url_prefix='/admin')

    # UI routes
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory('../frontend/pages', 'login.html')

    @app.route('/pages/<path:filename>')
    def pages(filename):
        from flask import send_from_directory
        return send_from_directory('../frontend/pages', filename)

    @app.route('/css/<path:filename>')
    def css(filename):
        from flask import send_from_directory
        return send_from_directory('../frontend/css', filename)

    @app.route('/js/<path:filename>')
    def js(filename):
        from flask import send_from_directory
        return send_from_directory('../frontend/js', filename)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Not found", "data": []}), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return jsonify({"success": False, "message": "Server error", "data": []}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)