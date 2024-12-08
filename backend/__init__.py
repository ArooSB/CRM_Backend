from calendar import calendar
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging
from logging import FileHandler, Formatter
from backend.config import Config
from flask_swagger_ui import get_swaggerui_blueprint

# Initialize the Flask extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

SWAGGER_URL = "/api/docs"
API_URL = "/static/users.json"



def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'Users API'
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # Register blueprints
    register_blueprints(app)

    # Register custom error handlers
    register_error_handlers(app)

    # Set up logging
    setup_logging(app)

    app.logger.info("🚀 Application started successfully.")

    @app.route('/')
    def index():
        app.logger.info("📥 Accessed index route")
        return jsonify({"message": "Welcome to the CRM API!"})

    return app

def register_blueprints(app):
    """Register application blueprints."""
    try:
        from routes import customers, workers, sales_leads, interactions, support_tickets, analytics, revenue
        app.register_blueprint(customers.bp)
        app.register_blueprint(workers.bp)
        app.register_blueprint(sales_leads.bp)
        app.register_blueprint(interactions.bp)
        app.register_blueprint(support_tickets.bp)
        app.register_blueprint(analytics.bp)
        app.resgister_blueprint(revenue.bp)
        app.register_blueprint(calendar.bp)
        app.logger.info("✅ Blueprints registered successfully.")
    except ImportError as e:
        app.logger.error(f"❌ Error registering blueprints: {e}")
        raise

def register_error_handlers(app):
    """Register custom error handlers."""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"⚠️ 404 Not Found: {error}")
        return jsonify({"message": "Resource not found!"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"❌ 500 Internal Server Error: {error}")
        return jsonify({"message": "Internal server error!"}), 500

    app.logger.info("✅ Custom error handlers registered.")

def setup_logging(app):
    """Configure application logging."""
    if not app.debug:
        file_handler = FileHandler("app.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(Formatter(
            "%(asctime)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("✅ Logging configured successfully.")
