# Empty file to make the directory a Python package

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS

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

    # Initialize cache with app
    cache.init_app(
        app,
        config={
            "CACHE_TYPE": "SimpleCache",  # Use simple cache for development
            "CACHE_DEFAULT_TIMEOUT": 300,
        },
    )

    # Add SQLAlchemy configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,  # Recycle connections every 5 minutes
    }

    # Initialize CORS only if CORS_RESOURCES is configured
    # Allow all CORS requests for now
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
    from app import properties, users

    app.register_blueprint(properties.bp, url_prefix="/api/properties")
    app.register_blueprint(users.bp, url_prefix="/api/users")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
