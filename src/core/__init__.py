from flask import current_app
from src.infrastructure.external.cinetpay_provider import CinetPayProvider
from src.core.repositories.house_repository import HouseOwnerRepository, HouseRepository
from src.core.repositories.payment_repository import PaymentRepository
from src.core.repositories.tenant_repository import TenantRepository
from src.core.repositories.user_repository import UserRepository
from src.core.services.house_service import HouseService, TenantService
from src.core.services.payment_service import PaymentService
from src.core.services.user_service import UserService


from src.core.services.notification_service import NotificationService
from src.infrastructure.external.sms_service import SMSService


def get_payment_service():
    # Use site-id and api-key from config
    site_id = current_app.config.get("CINETPAY_SITE_ID")
    api_key = current_app.config.get("CINETPAY_API_KEY")

    provider = CinetPayProvider(api_key, site_id) if site_id and api_key else None
    repository = PaymentRepository()

    return PaymentService(repository, provider)


def get_user_service():
    repository = UserRepository()
    return UserService(repository)


def get_house_service():
    house_repo = HouseRepository()
    owner_repo = HouseOwnerRepository()
    tenant_repo = TenantRepository()
    return HouseService(house_repo, owner_repo, tenant_repo)


def get_tenant_service():
    tenant_repo = TenantRepository()
    return TenantService(tenant_repo)


def get_notification_service():
    sms_api_key = current_app.config.get("SMS_API_KEY")
    sms_api_token = current_app.config.get("SMS_API_TOKEN")
    sms_base_url = current_app.config.get("SMS_BASE_URL")
    sms_sender_id = current_app.config.get("SMS_SENDER_ID")

    sms_service = None
    if all([sms_api_key, sms_api_token, sms_base_url, sms_sender_id]):
        sms_service = SMSService(
            sms_api_key, sms_api_token, sms_base_url, sms_sender_id
        )

    return NotificationService(sms_service)
