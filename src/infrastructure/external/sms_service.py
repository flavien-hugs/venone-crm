import requests
import logging

logger = logging.getLogger(__name__)


class SMSService:
    def __init__(self, api_key: str, api_token: str, base_url: str, sender_id: str):
        self.api_key = api_key
        self.api_token = api_token
        self.base_url = base_url
        self.sender_id = sender_id

    def send_sms(self, to: str, message: str) -> bool:
        """
        Send an SMS via the configured gateway.
        """
        if not all([self.api_key, self.api_token, self.base_url, self.sender_id]):
            logger.error("SMS service not fully configured.")
            return False

        payload = {
            "api_key": self.api_key,
            "api_token": self.api_token,
            "to": to,
            "from": self.sender_id,
            "message": message,
        }

        try:
            response = requests.post(f"{self.base_url}/send", json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"SMS successfully sent to {to}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS to {to}: {e}")
            return False
