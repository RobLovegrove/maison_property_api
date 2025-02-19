# Empty file to make the directory a Python package

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import config

# Initialize extensions without app context
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name="default"):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config[config_name])

    @app.before_request
    def log_request_info():
        app.logger.debug("Headers: %s", request.headers)
        app.logger.debug("Body: %s", request.get_data())
        app.logger.debug("URL: %s", request.url)

    # Configure CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5137",
                    "https://www.maisonai.co.uk",
                    "http://localhost:3000",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints/routes
    from app.properties import bp as properties_bp

    app.register_blueprint(properties_bp, url_prefix="/api/properties")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    # Print registered routes for debugging
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    print("\n")

    return app
