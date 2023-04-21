from datetime import datetime
from datetime import timedelta

from src import db
from src.celery import celery_app
from src.main.utils import send_sms_reminder
from src.tenant import VNHouse

from celery import shared_task


@shared_task
def payment_reminders():
    current_date = datetime.utcnow().date()
    houses = VNHouse.query.filter_by(vn_house_is_open=True).all()

    for house in houses:
        reminder_date = house.vn_house_lease_end_date - timedelta(days=7)
        if current_date == reminder_date:
            for tenant in house.tenants:
                send_sms_reminder(house, tenant)


@shared_task
def update_expired_lease_end_dates():

    current_date = datetime.utcnow().date()

    expired_houses = VNHouse.query.filter(
        VNHouse.vn_house_is_open,
        VNHouse.vn_house_lease_end_date <= current_date,
    ).all()

    for house in expired_houses:
        house.update_lease_end_date()
    db.session.commit()


@shared_task
def payment_reminders_for_expired_leases():
    current_date = datetime.utcnow().date()
    expired_houses = VNHouse.query.filter(
        VNHouse.vn_house_is_open,
        VNHouse.vn_house_lease_end_date <= current_date,
    ).all()

    for house in expired_houses:
        reminder_date = house.vn_house_lease_end_date - timedelta(days=7)
        celery_app.send_task(
            "src.tenant.tasks.payment_reminders",
            args=[],
            kwargs={"house_id": house.id},
            eta=reminder_date,
        )
