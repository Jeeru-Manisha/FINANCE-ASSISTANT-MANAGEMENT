import os
from datetime import timedelta

class Config:
    """Configuration class for the Finance Assistant application"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    BCRYPT_LOG_ROUNDS = 13
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///finance_assistant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # API Settings
    MAX_CONCURRENT_USERS = 5000
    QUERY_RESPONSE_TIME = 2  # seconds
    DATA_PROCESSING_TIME = 5  # seconds
    
    # Banking API (Example - would be replaced with actual banking APIs)
    OPEN_BANKING_BASE_URL = "https://api.example-bank.com/v1"
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Security Headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'