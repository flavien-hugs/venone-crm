import os
import logging as lg

from src import create_venone_app, db
from src.auth.models import VNRole, VNUser

from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade

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
