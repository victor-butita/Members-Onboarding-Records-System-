import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from a2wsgi import ASGIMiddleware
from main import app

# Passenger requires a callable named 'application' (WSGI)
application = ASGIMiddleware(app)
