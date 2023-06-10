from src import celery_init_app
from src.venone import venone_app

from celery.schedules import crontab

celery_app = celery_init_app(venone_app)
celery_app.autodiscover_tasks(["src.tenant.tasks", "src.payments.tasks"])

celery_app.conf.beat_schedule = {
    "payment_reminders_for_expired_leases": {
        "task": "src.tenant.tasks.payment_reminders_for_expired_leases",
        "schedule": crontab(minute="*/60"),
    },
    "check_transaction_trx": {
        "task": "src.payments.tasks.check_transaction_trx",
        "schedule": crontab(minute="*/60"),
    },
}
