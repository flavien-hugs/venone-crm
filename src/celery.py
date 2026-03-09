from celery.schedules import crontab
from src.infrastructure.config.celery_config import celery_init_app
from src.main import create_app
import os

# Create the flask app instance for celery workers
config_name = os.environ.get("FLASK_CONFIG", "dev")
app = create_app(config_name)

# Initialize celery
celery_app = celery_init_app(app)
celery_app.autodiscover_tasks(["src.infrastructure.tasks"])

celery_app.conf.beat_schedule = {
    "payment_reminders_for_expired_leases": {
        "task": "src.infrastructure.tasks.celery_tasks.payment_reminders_for_expired_leases",
        "schedule": crontab(minute="*/60"),
    },
    "check_transaction_trx": {
        "task": "src.infrastructure.tasks.celery_tasks.check_transaction_trx",
        "schedule": crontab(minute="*/60"),
    },
}
