# Empty file to make the directory a Python package

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    CORS(flask_app)

    # Register blueprints/routes
    from app.main import bp
    flask_app.register_blueprint(bp)

    return flask_app


# Create the app instance
app = create_app()
