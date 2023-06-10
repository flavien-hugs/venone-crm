import logging
from datetime import datetime

from src.exts import db
from src.main.utils import send_sms_reminder
from src.tenant import VNHouse

from celery import shared_task
from celery import signature

logger = logging.getLogger(__name__)


@shared_task
def payment_reminders(vn_house_id):

    current_date = datetime.utcnow().date()

    house = VNHouse.query.get(vn_house_id)

    if not house:
        logger.info(f"House with ID {vn_house_id} not found.")
        return

    if not house.vn_house_is_open:
        logger.info(f"House {vn_house_id} is not open.")
        return

    if house.vn_house_lease_end_date > current_date:
        logger.info(f"House {vn_house_id} lease is not expired.")
        return

    if house.vn_house_is_open:
        logger.info(f"House status: {house.vn_house_is_open}")
        tenant = house.house_tenants[0] if house.house_tenants else None
        send_sms_reminder(house, tenant)
        if house.vn_house_lease_end_date <= current_date:
            house.update_lease_end_date()
            
        db.session.commit()


@shared_task
def payment_reminders_for_expired_leases():
    current_date = datetime.utcnow().date()

    expired_houses = VNHouse.query.filter(
        VNHouse.vn_house_is_open == True,
        VNHouse.vn_house_lease_end_date <= current_date,
    ).all()

    logger.info(f"Found {len(expired_houses)} expired houses.")

    for house in expired_houses:
        reminder_date = house.vn_house_lease_end_date
        logger.info(f"Reminder date {reminder_date} expired houses.")
        payment_reminder_task = signature(
            "src.tenant.tasks.payment_reminders", kwargs={"vn_house_id": house.id}
        )
        payment_reminder_task.apply_async(eta=reminder_date)
