import logging
from datetime import datetime

from celery import shared_task, signature
from src.core import get_house_service, get_notification_service, get_payment_service
from src.infrastructure.config.plugins import db

logger = logging.getLogger(__name__)


@shared_task
def check_transaction_trx():
    """
    Checks all pending payments and verifies them with the payment provider.
    """
    try:
        payment_service = get_payment_service()
        payment_service.verify_all_pending_payments()
    except Exception as e:
        logger.exception("Error during scheduled transaction verification: %s", e)
        raise e


@shared_task
def payment_reminders(vn_house_id):
    """
    Sends a payment reminder SMS for a specific house if lease is expired.
    """
    current_date = datetime.utcnow().date()
    house_service = get_house_service()
    payment_service = get_payment_service()
    notification_service = get_notification_service()

    house = house_service.house_repo.model.query.get(vn_house_id)

    if not house:
        logger.info(f"House with ID {vn_house_id} not found.")
        return

    if not house.vn_house_is_open:
        logger.info(f"House {vn_house_id} is not open.")
        return

    # Generate payment URL
    payment_url = payment_service.initiate_payment_url(house)
    if not payment_url:
        logger.warning(f"Could not generate payment URL for house {vn_house_id}")
        return

    logger.info(f"Sending reminder for House {vn_house_id}")
    tenant = house.house_tenants[0] if house.house_tenants else None
    if tenant:
        notification_service.send_payment_reminder(house, tenant, payment_url)

    if house.vn_house_lease_end_date <= current_date:
        house_service.update_lease_end_date_if_expired(house.id)

    db.session.commit()


@shared_task
def payment_reminders_for_expired_leases():
    """
    Periodic task to find all expired leases and schedule individual reminders.
    """
    current_date = datetime.utcnow().date()
    house_service = get_house_service()

    expired_houses = house_service.house_repo.find_expired_leases(current_date)
    logger.info(f"Found {len(expired_houses)} expired houses.")

    for house in expired_houses:
        reminder_date = house.vn_house_lease_end_date
        logger.info(f"Scheduling reminder for house {house.id} at {reminder_date}")

        payment_reminder_task = signature(
            "src.infrastructure.tasks.celery_tasks.payment_reminders",
            kwargs={"vn_house_id": house.id},
        )
        payment_reminder_task.apply_async(eta=reminder_date)
