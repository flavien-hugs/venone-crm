import logging

import pyshorteners

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, sms_service=None):
        self.sms_service = sms_service

    def send_payment_reminder(self, house_model, tenant_model, payment_url: str):
        if not self.sms_service:
            logger.warning("No SMS service configured for notifications.")
            return False

        try:
            s = pyshorteners.Shortener()
            short_url = s.dagd.short(payment_url)
        except Exception as e:
            logger.warning(f"Error shortening URL: {e}. Using original URL.")
            short_url = payment_url

        fullname = tenant_model.vn_fullname
        house_lease_end = house_model.vn_house_lease_end_date
        message = (
            f"Bonjour {fullname}, votre loyer du mois de {house_lease_end} est prête. "
            f"Veuillez cliquer sur ce lien: {short_url} pour procéder au paiement. Merci, Venone."
        )

        return self.sms_service.send_sms(tenant_model.vn_phonenumber_one, message)
