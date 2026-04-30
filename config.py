import os
import urllib.parse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_change_in_prod'
    
    # Database Configuration
    # Format: mysql+mysqlconnector://username:password@hostname/databasename
    # User must replace these credentials
    DB_USER = 'root'
    DB_PASS = 'R@j@t2004'
    DB_HOST = 'localhost'
    DB_NAME = 'library'
    
    # URL encode password to handle special characters like '@'
    _encoded_pass = urllib.parse.quote_plus(DB_PASS)
    
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{_encoded_pass}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key_change_in_prod'
    
    # Pagination
    ITEMS_PER_PAGE = 10
