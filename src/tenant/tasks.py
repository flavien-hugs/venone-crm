from datetime import datetime
from datetime import timedelta

from celery import shared_task
from src.main.routes import send_sms_reminder
from src.mixins.email import send_email_reminder
from src.tenant import VNHouse


@shared_task
def payment_reminders():

    current_date = datetime.utcnow().date()
    houses = VNHouse.query.filter_by(vn_house_is_open=True).all()

    for house in houses:
        reminder_date = house.vn_house_lease_end_date - timedelta(days=7)
        if current_date <= reminder_date:
            for tenant in house.tenants:
                send_sms_reminder(house, tenant)
                send_email_reminder(tenant, house)
