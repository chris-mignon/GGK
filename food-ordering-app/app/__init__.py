from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """Application Factory."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_ordering_app.db'
    app.config['SECRET_KEY'] = 'replace_with_a_secure_secret_key'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    Bootstrap(app)

    # Register Blueprints
    from .routes.admin_routes import admin_bp
    from .routes.customer_routes import customer_bp
    from .routes.delivery_routes import delivery_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(delivery_bp, url_prefix='/delivery')

    return app