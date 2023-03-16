import os
import requests
from datetime import date, timedelta

from flask import current_app

from celery import shared_task

from src.payment import VNPayment
from src.tenant import VNHouse, VNTenant
from src.main.routes import send_sms_reminder


@shared_task
def send_payment_reminders():
    """
    Envoie un email de rappel de paiement à tous les locataires pour chaque propriété
    """

    houses = VNHouse.query.filter_by(vn_house_is_open=True).all()

    for house in houses:
        tenant = house.get_current_tenant()
        send_sms_reminder(house, tenant)
