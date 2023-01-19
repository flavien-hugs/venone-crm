import logging as lg
import os

from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_migrate import upgrade
from src import create_venone_app
from src import db
from src.auth.models import VNRole
from src.auth.models import VNUser

dotenv_path = os.path.join(os.path.dirname(__file__), ".flaskenv")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


venone_app = create_venone_app(os.getenv("FLASK_CONFIG") or "dev")
migrate = Migrate(venone_app, db, render_as_batch=True)


@venone_app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        user=VNUser,
    )


@venone_app.cli.command("init_db")
def init_db():
    upgrade()
    db.create_all()
    VNRole.insert_roles()
    db.session.commit()
    lg.warning("Database initialized !")


if __name__ == "__main__":
    venone_app.run()
