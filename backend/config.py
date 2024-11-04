import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aroo'
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5433/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
