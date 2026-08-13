import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def database_uri():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return f"sqlite:///{(BASE_DIR / 'hostel_laundry.db').as_posix()}"
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-this-secret')
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
