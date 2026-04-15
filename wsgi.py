import sys
import os

# Add the backend folder to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Now import from backend/app.py
from app import create_app

# Create app
app = create_app()

# This is for Vercel
application = app

if __name__ == "__main__":
    app.run()
