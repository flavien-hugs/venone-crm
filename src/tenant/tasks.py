from datetime import datetime
from datetime import timedelta

from celery import shared_task
from flask import current_app
from src import celery_init_app
from src import db
from src.main.utils import send_sms_reminder
from src.tenant import VNHouse

# from src.mixins.email import send_email_reminder


@shared_task
def payment_reminders():

    current_date = datetime.utcnow().date()
    houses = VNHouse.query.filter_by(vn_house_is_open=True).all()

    for house in houses:
        reminder_date = house.vn_house_lease_end_date - timedelta(days=7)
        if current_date <= reminder_date:
            for tenant in house.tenants:
                send_sms_reminder(house, tenant)
                # send_email_reminder(tenant, house)


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
