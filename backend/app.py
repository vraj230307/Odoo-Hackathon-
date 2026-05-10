from flask import Flask
from flask_cors import CORS

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.dashboard_routes import dashboard_bp
from routes.trip_routes import trip_bp
from routes.itinerary_routes import itinerary_bp
from routes.city_routes import city_bp
from routes.budget_routes import budget_bp
from routes.notes_routes import notes_bp
from routes.packing_routes import packing_bp
from routes.sharing_routes import sharing_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp,      url_prefix="/api")
app.register_blueprint(user_bp,      url_prefix="/api")
app.register_blueprint(dashboard_bp, url_prefix="/api")
app.register_blueprint(trip_bp,      url_prefix="/api")
app.register_blueprint(itinerary_bp, url_prefix="/api")
app.register_blueprint(city_bp,      url_prefix="/api")
app.register_blueprint(budget_bp,    url_prefix="/api")
app.register_blueprint(notes_bp,     url_prefix="/api")
app.register_blueprint(packing_bp,   url_prefix="/api")
app.register_blueprint(sharing_bp,   url_prefix="/api")
app.register_blueprint(admin_bp,     url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)