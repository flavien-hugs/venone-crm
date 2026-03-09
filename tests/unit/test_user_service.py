import pytest
from unittest.mock import Mock, patch

from src.core.services.user_service import UserService
from src.core.repositories.user_repository import UserRepository
from src.core.domain.entities.user import UserEntity


@pytest.fixture
def mock_user_repository():
    """Fixture for a mock UserRepository."""
    return Mock(spec=UserRepository)


@pytest.fixture
def user_service(mock_user_repository):
    """Fixture for UserService with a mocked repository."""
    return UserService(mock_user_repository)


@pytest.fixture
def sample_user_entity():
    """Fixture for a sample UserEntity."""
    return UserEntity(
        id=1,
        uuid="test-uuid-123",
        fullname="Test User",
        email="test@example.com",
        phone="123456789",
        country="SN",
        balance=5000.0,
        is_house_owner=True,
        is_company=False,
        is_administrator=False,
        owner_percent=10.0,
        company_percent=5.0,
    )


def test_get_total_payments_received_user_not_found(user_service, mock_user_repository):
    """Test get_total_payments_received when the user is not found."""
    mock_user_repository.get_by_id.return_value = None
    total = user_service.get_total_payments_received(user_id=999)
    assert total == 0.0


@patch("src.core.services.user_service.db")
def test_get_total_payments_received_for_owner(
    mock_db, user_service, mock_user_repository, sample_user_entity
):
    """Test get_total_payments_received for a house owner."""
    mock_user_repository.get_by_id.return_value = sample_user_entity

    # Mock the database query and its result
    mock_db.session.query.return_value.filter.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.scalar.return_value = (  # noqa: E501
        150000.0
    )

    total = user_service.get_total_payments_received(user_id=1)

    assert total == 150000.0
    mock_user_repository.get_by_id.assert_called_once_with(1)


def test_calculate_amount_apply_percent_user_not_found(
    user_service, mock_user_repository
):
    """Test calculate_amount_apply_percent when the user is not found."""
    mock_user_repository.get_by_id.return_value = None
    result = user_service.calculate_amount_apply_percent(user_id=999)
    assert result == 0.0


@patch("src.core.services.user_service.House")
def test_calculate_amount_apply_percent_for_owner(
    mock_house, user_service, mock_user_repository, sample_user_entity
):
    """Test calculate_amount_apply_percent for a house owner."""
    mock_user_repository.get_by_id.return_value = sample_user_entity

    # Mock the houses and their rents
    house1 = Mock(vn_house_rent=100000)
    house2 = Mock(vn_house_rent=200000)
    mock_house.query.filter_by.return_value.all.return_value = [house1, house2]

    # 10% of (100000 + 200000) = 30000
    expected_percent = (100000 + 200000) * (10.0 / 100)

    result = user_service.calculate_amount_apply_percent(user_id=1)

    assert result == expected_percent
    mock_user_repository.get_by_id.assert_called_once_with(1)


def test_get_dashboard_stats_user_not_found(user_service, mock_user_repository):
    """Test get_dashboard_stats when the user is not found."""
    mock_user_repository.get_by_id.return_value = None
    stats = user_service.get_dashboard_stats(user_id=999)
    assert stats == {}


@patch("src.core.services.user_service.Payment")
@patch("src.core.services.user_service.House")
@patch("src.core.services.user_service.Tenant")
@patch("src.core.services.user_service.HouseOwner")
@patch("src.core.services.user_service.TransferRequest")
def test_get_dashboard_stats_for_user(
    mock_transfer,
    mock_owner,
    mock_tenant,
    mock_house,
    mock_payment,
    user_service,
    mock_user_repository,
    sample_user_entity,
):
    """Test get_dashboard_stats for a regular user."""
    mock_user_repository.get_by_id.return_value = sample_user_entity

    # Mock counts for each model
    mock_payment.query.filter_by.return_value.count.return_value = 5
    mock_house.query.filter_by.return_value.count.side_effect = [
        2,
        1,
        1,
    ]  # houses_count, houses_close_count, houses_open_count
    mock_tenant.query.filter_by.return_value.count.return_value = 3
    mock_owner.query.filter_by.return_value.count.return_value = 1
    mock_transfer.query.filter_by.return_value.count.return_value = 2

    stats = user_service.get_dashboard_stats(user_id=1)

    expected_stats = {
        "payments_count": 5,
        "houses_count": 2,
        "houses_close_count": 1,
        "houses_open_count": 1,
        "tenants_count": 3,
        "owners_count": 1,
        "transfers_count": 2,
    }

    assert stats == expected_stats
    mock_user_repository.get_by_id.assert_called_once_with(1)
