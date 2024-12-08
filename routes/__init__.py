from flask import Flask
from routes.analytics import bp as analytics_bp
from routes.customers import bp as customers_bp
from routes.interactions import bp as interactions_bp
from routes.sales_leads import bp as sales_leads_bp
from routes.support_tickets import bp as support_tickets_bp
from routes.workers import bp as workers_bp
from routes.revenue import bp as revenue_bp

def register_routes(app: Flask):

    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(customers_bp, url_prefix='/api')
    app.register_blueprint(interactions_bp, url_prefix='/api')
    app.register_blueprint(sales_leads_bp, url_prefix='/api')
    app.register_blueprint(support_tickets_bp, url_prefix='/api')
    app.register_blueprint(workers_bp, url_prefix='/api')
    app.register_blueprint(revenue_bp, url_prefix='/api')