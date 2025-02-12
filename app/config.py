from dotenv import load_dotenv
import os

load_dotenv()

url = "DATABASE_URL"
postgres = "postgresql:///property_db"


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(url, postgres)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
