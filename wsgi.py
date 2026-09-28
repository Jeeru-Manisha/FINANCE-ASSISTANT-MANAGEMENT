import sys
import os

# Add project directory to Python path
path = os.path.dirname(os.path.abspath(__file__))

if path not in sys.path:
    sys.path.insert(0, path)

from finance_app import app, init_db

# Initialize database
init_db()

application = app