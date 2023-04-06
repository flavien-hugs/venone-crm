from celery.schedules import crontab

from src.venone import venone_app
from src import celery_init_app

celery_app = celery_init_app(venone_app)
celery_app.autodiscover_tasks(["src.tenant.tasks"])

celery_app.conf.beat_schedule = {
    "update_expired_lease_end_dates": {
        "task": "src.tenant.tasks.update_expired_lease_end_dates",
        "schedule": crontab(hour=0, minute=0, day_of_week='*'),
    },
    "payment_reminders_for_expired_leases": {
        "task": "src.tenant.tasks.payment_reminders_for_expired_leases",
        "schedule": crontab(day_of_month="*/31"),
    },
}
