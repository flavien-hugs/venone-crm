import pytest
from unittest.mock import Mock, patch

from src.core.services.payment_service import PaymentService
from src.core.repositories.payment_repository import PaymentRepository
from src.core.interfaces.payment_provider import IPaymentProvider
from src.infrastructure.persistence.models import Payment, User, Tenant


@pytest.fixture
def mock_payment_repository():
    """Fixture for a mock PaymentRepository."""
    return Mock(spec=PaymentRepository)


@pytest.fixture
def mock_payment_provider():
    """Fixture for a mock IPaymentProvider."""
    return Mock(spec=IPaymentProvider)


@pytest.fixture
def payment_service(mock_payment_repository, mock_payment_provider):
    """Fixture for PaymentService with mocked dependencies."""
    return PaymentService(mock_payment_repository, mock_payment_provider)


def test_verify_payment_with_provider_success(
    app_context, payment_service, mock_payment_repository, mock_payment_provider
):
    """Test payment verification with a successful provider response."""
    payment = Mock(spec=Payment)
    mock_payment_repository.find_by_transaction_id.return_value = payment
    mock_payment_provider.verify_transaction.return_value = {"status": "SUCCESS"}

    with patch("src.core.services.payment_service.db") as mock_db:
        payment_service.verify_payment_with_provider("TRX123")

        assert payment.vn_pay_status is True
        mock_db.session.commit.assert_called_once()


def test_verify_payment_with_provider_failed(
    app_context, payment_service, mock_payment_repository, mock_payment_provider
):
    """Test payment verification with a failed provider response."""
    payment = Mock(spec=Payment)
    payment.vn_pay_status = False  # Initialize the attribute
    mock_payment_repository.find_by_transaction_id.return_value = payment
    mock_payment_provider.verify_transaction.return_value = {"status": "FAILED"}

    with patch("src.core.services.payment_service.db") as mock_db:
        payment_service.verify_payment_with_provider("TRX456")

        assert not payment.vn_pay_status
        mock_db.session.commit.assert_not_called()


@patch("src.core.get_house_service")
@patch("src.core.services.payment_service.Tenant")
def test_initiate_payment_url_success(
    mock_tenant,
    mock_get_house_service,
    app_context,
    payment_service,
    mock_payment_provider,
):
    """Test successful initiation of a payment URL."""
    mock_house_service = Mock()
    mock_get_house_service.return_value = mock_house_service
    mock_house_service.get_current_tenant_id.return_value = 1

    mock_tenant.query.get.return_value = Mock(spec=Tenant, vn_fullname="Test Tenant")

    mock_user = Mock(spec=User, vn_device="XOF")
    mock_house_model = Mock()
    mock_house_model.id = 10
    mock_house_model.vn_house_id = "H123"
    mock_house_model.vn_house_rent = 150000.0
    mock_house_model.user_houses = mock_user

    mock_payment_provider.initiate_payment.return_value = {
        "code": "201",
        "data": {"payment_url": "http://example.com/pay"},
    }

    with patch("src.core.services.payment_service.Payment"), patch(
        "src.core.services.payment_service.db"
    ):
        payment_url = payment_service.initiate_payment_url(mock_house_model)

        assert payment_url == "http://example.com/pay"
        mock_payment_provider.initiate_payment.assert_called_once()


@patch("src.core.get_house_service")
def test_initiate_payment_url_failure(
    mock_get_house_service, app_context, payment_service, mock_payment_provider
):
    """Test failed initiation of a payment URL."""
    mock_house_service = Mock()
    mock_get_house_service.return_value = mock_house_service

    mock_user = Mock(spec=User, vn_device="XOF")
    mock_house_model = Mock()
    mock_house_model.user_houses = mock_user
    mock_payment_provider.initiate_payment.return_value = {"code": "500"}

    with patch("src.core.services.payment_service.Tenant"):
        payment_url = payment_service.initiate_payment_url(mock_house_model)

    assert payment_url is None
