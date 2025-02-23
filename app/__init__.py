# Empty file to make the directory a Python package

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
cache = Cache()


def create_app(config_name="development"):
    """Create Flask application."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Configure app
    if config_name == "production":
        app.config.from_object("config.ProductionConfig")
    elif config_name == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    # Initialize extensions with app
    db.init_app(app)

    # Add SQLAlchemy configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,  # Recycle connections every 5 minutes
    }

    # Register blueprints
    from app.properties import bp as properties_bp

    app.register_blueprint(properties_bp, url_prefix="/api/properties")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
