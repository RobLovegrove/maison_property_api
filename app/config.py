import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "..", "migrations")

    # Add CORS configuration
    CORS_HEADERS = "Content-Type"
    CORS_RESOURCES = {
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:5137",
                "http://www.maisonai.co.uk",
                "https://www.maisonai.co.uk",
                "http://maisonbot-api.xyz",
                "https://maisonbot-api.xyz",
                "http://4.207.106.67",
                "http://128.251.124.181",
                "https://maison-frontend.azurewebsites.net",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    }


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/test_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

SEED_PROPERTY_IMAGES = [
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
]

SEED_ADDITIONAL_IMAGES = [
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
    "https://maisonblobstorage.blob.core.windows.net/"
    "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg",
]

SEED_FLOORPLAN_URL = (
    "https://wpmedia.roomsketcher.com/content/uploads/2022/01/"
    "06150346/2-Bedroom-Home-Plan-With-Dimensions.png"
)
