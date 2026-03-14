import sys
import os

# Adds the current directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import the application factory
from app import create_app

# Create the application object for the WSGI server
application = create_app()
