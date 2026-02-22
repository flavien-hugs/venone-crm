from celery.schedules import crontab

from src import celery_init_app
from src.venone import venone_app

celery_app = celery_init_app(venone_app)
celery_app.autodiscover_tasks(["src.tenant.tasks", "src.payment.tasks"])

celery_app.conf.beat_schedule = {
    "payment_reminders_for_expired_leases": {
        "task": "src.tenant.tasks.payment_reminders_for_expired_leases",
        "schedule": crontab(minute="*/60"),
    },
    "check_transaction_trx": {
        "task": "src.payment.tasks.check_transaction_trx",
        "schedule": crontab(minute="*/60"),
    },
}
