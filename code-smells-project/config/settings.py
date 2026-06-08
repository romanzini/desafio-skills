import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-CHANGE-IN-PRODUCTION')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'loja.db')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
