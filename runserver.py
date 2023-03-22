import logging as lg
import os

from celery import schedules
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_migrate import upgrade
from src import celery_init_app
from src import create_venone_app
from src import db
from src.auth.models import VNRole
from src.auth.models import VNUser
from src.payment.models import VNPayment
from src.tenant.models import VNHouse
from src.tenant.models import VNHouseOwner
from src.tenant.models import VNTenant

dotenv_path = os.path.join(os.path.dirname(__file__), ".flaskenv")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

venone_app = create_venone_app(os.getenv("FLASK_CONFIG") or "dev")
celery_app = celery_init_app(venone_app)
celery_app.conf.beat_schedule = {
    "check_due_dates": {
        "task": "payment_reminders",
        "schedule": schedules.crontab(hour="*"),
    }
}

migrate = Migrate(venone_app, db, render_as_batch=True)


@venone_app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        user=VNUser,
        tenant=VNTenant,
        house=VNHouse,
        houseowner=VNHouseOwner,
        payment=VNPayment,
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
