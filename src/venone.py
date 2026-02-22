import os

from src import create_venone_app

venone_app = create_venone_app(os.getenv("FLASK_CONFIG") or "dev")
