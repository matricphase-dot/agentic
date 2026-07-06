import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///data/agentic.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
