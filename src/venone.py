from dotenv import dotenv_values
from src import create_venone_app

env = dotenv_values(".flaskenv")
venone_app = create_venone_app(env.get("FLASK_CONFIG") or "dev")
