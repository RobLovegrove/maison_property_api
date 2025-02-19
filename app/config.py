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


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "postgresql://roblovegrove@localhost:5432/test_db"
    )


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
    "https://webberstudio.com/wp-content/uploads/2023/02/"
    "Stunning-House-Design.jpg",
    "https://static.schumacherhomes.com/umbraco/media/wvflutbh/"
    "image4.jpg?format=webp",
    "https://media.architecturaldigest.com/photos/61b0ce48dccdb75fa170f8f7/"
    "16:9/w_2560%2Cc_limit/PurpleCherry_Williams_0012.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8S9I5BU7fzueWmpn"
    "ELDz5f7WZ70_pcDfMIw&s",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVAsvbLdqmTr0y0Kh"
    "DlNNBBJ0ZQldPgFs9sw&s",
]

SEED_ADDITIONAL_IMAGES = [
    "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?fm=jpg&q=60"
    "&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8aG9tZSUyMGludGVy"
    "aW9yfGVufDB8fDB8fHww",
    "https://images.livspace-cdn.com/w:3840/plain/https://d3gq2merok8n5r."
    "cloudfront.net/abhinav/design-ideas-thumbnails-1628773921-7vSz1/jas-"
    "thumbnails-1662014793-zEzY3/mobile-1662014804-Sebbn/mbr-m-1662025089"
    "-SomZl.png",
    "https://s3.amazonaws.com/buildercloud/1a5e7ed6587ee905ab32d94ed23432fb."
    "jpeg",
    "https://st.hzcdn.com/simgs/f801330c079635d3_14-7430/home-design.jpg",
    "https://www.thesmallgardener.co.uk/wp-content/uploads/2023/03/"
    "Home-page.jpg",
]

SEED_FLOORPLAN_URL = (
    "https://wpmedia.roomsketcher.com/content/uploads/2022/01/"
    "06150346/2-Bedroom-Home-Plan-With-Dimensions.png"
)
