from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging
from logging import FileHandler

from backend.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    register_blueprints(app)
    register_error_handlers(app)
    setup_logging(app)  # Set up logging
    return app

def register_blueprints(app):
    """Register application blueprints."""
    from routes import customers, workers, sales_leads, interactions, support_tickets, analytics
    app.register_blueprint(customers.bp)
    app.register_blueprint(workers.bp)
    app.register_blueprint(sales_leads.bp)
    app.register_blueprint(interactions.bp)
    app.register_blueprint(support_tickets.bp)
    app.register_blueprint(analytics.bp)

def register_error_handlers(app):
    """Register custom error handlers."""
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"message": "Resource not found!"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal server error: {error}")
        return jsonify({"message": "Internal server error!"}), 500

def setup_logging(app):
    if not app.debug:
        file_handler = FileHandler('app.log')
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the CRM API!"})
