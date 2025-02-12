from flask_migrate import Migrate
from app.main import app
from app.models import db

migrate = Migrate(app, db)

if __name__ == '__main__':
    from flask.cli import FlaskGroup
    cli = FlaskGroup(app)
    cli() 