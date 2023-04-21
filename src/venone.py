import os

from dotenv import load_dotenv
from src import create_venone_app

dotenv_path = os.path.join(os.path.dirname(__file__), ".flaskenv")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

venone_app = create_venone_app(os.getenv("FLASK_CONFIG") or "dev")
