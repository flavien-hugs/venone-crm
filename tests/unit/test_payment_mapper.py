import pytest
from unittest.mock import Mock
from datetime import date

from src.core.mappers.payment_mapper import PaymentMapper
from src.core.domain.entities.payment import PaymentEntity
from src.infrastructure.persistence.models import Payment


@pytest.fixture
def mock_persistence_payment():
    """Fixture for a mock SQLAlchemy Payment model instance."""
    mock_payment = Mock(spec=Payment)
    mock_payment.id = 1
    mock_payment.vn_transaction_id = "TRX123"
    mock_payment.vn_pay_amount = 250000.0
    mock_payment.vn_pay_status = True
    mock_payment.vn_pay_date = date(2024, 3, 10)
    mock_payment.vn_house_id = 10
    mock_payment.vn_tenant_id = 20
    mock_payment.vn_payee_id = 30
    mock_payment.vn_cinetpay_data = {"some": "metadata"}
    return mock_payment


@pytest.fixture
def mock_domain_payment():
    """Fixture for a mock PaymentEntity domain instance."""
    return PaymentEntity(
        id=2,
        transaction_id="TRX456",
        amount=300000.0,
        status=False,
        date=date(2024, 4, 1),
        house_id=11,
        tenant_id=21,
        payee_id=31,
        metadata={"other": "data"},
    )


def test_to_domain_conversion(app_context, mock_persistence_payment):
    """Test that PaymentMapper correctly converts a persistence model to a domain entity."""
    domain_entity = PaymentMapper.to_domain(mock_persistence_payment)

    assert isinstance(domain_entity, PaymentEntity)
    assert domain_entity.id == mock_persistence_payment.id
    assert domain_entity.transaction_id == mock_persistence_payment.vn_transaction_id
    assert domain_entity.amount == mock_persistence_payment.vn_pay_amount
    assert domain_entity.status == mock_persistence_payment.vn_pay_status
    assert domain_entity.date == mock_persistence_payment.vn_pay_date
    assert domain_entity.house_id == mock_persistence_payment.vn_house_id
    assert domain_entity.tenant_id == mock_persistence_payment.vn_tenant_id
    assert domain_entity.payee_id == mock_persistence_payment.vn_payee_id
    assert domain_entity.metadata == mock_persistence_payment.vn_cinetpay_data


def test_to_persistence_conversion(app_context, mock_domain_payment):
    """Test that PaymentMapper correctly converts a domain entity to a persistence dictionary."""
    persistence_dict = PaymentMapper.to_persistence(mock_domain_payment)

    assert persistence_dict["vn_transaction_id"] == mock_domain_payment.transaction_id
    assert persistence_dict["vn_pay_amount"] == mock_domain_payment.amount
    assert persistence_dict["vn_pay_status"] == mock_domain_payment.status
    assert persistence_dict["vn_pay_date"] == mock_domain_payment.date
    assert persistence_dict["vn_house_id"] == mock_domain_payment.house_id
    assert persistence_dict["vn_tenant_id"] == mock_domain_payment.tenant_id
    assert persistence_dict["vn_payee_id"] == mock_domain_payment.payee_id
    assert persistence_dict["vn_cinetpay_data"] == mock_domain_payment.metadata
