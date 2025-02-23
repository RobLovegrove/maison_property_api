import os

class Config:
    """Base config."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

class ProductionConfig(Config):
    """Production config."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development config."""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing config."""
    FLASK_ENV = 'testing'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False 