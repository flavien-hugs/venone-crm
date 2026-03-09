import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta

from src.core.services.house_service import HouseService
from src.core.repositories.house_repository import HouseRepository, HouseOwnerRepository
from src.core.repositories.tenant_repository import TenantRepository
from src.infrastructure.persistence.models import House, Tenant


@pytest.fixture
def mock_house_repository():
    """Fixture for a mock HouseRepository."""
    return Mock(spec=HouseRepository)


@pytest.fixture
def mock_owner_repository():
    """Fixture for a mock HouseOwnerRepository."""
    return Mock(spec=HouseOwnerRepository)


@pytest.fixture
def mock_tenant_repository():
    """Fixture for a mock TenantRepository."""
    return Mock(spec=TenantRepository)


@pytest.fixture
def house_service(mock_house_repository, mock_owner_repository, mock_tenant_repository):
    """Fixture for HouseService with mocked repositories."""
    return HouseService(
        mock_house_repository, mock_owner_repository, mock_tenant_repository
    )


def test_update_lease_end_date_if_expired(
    app_context, house_service, mock_house_repository
):
    """Test that lease end date is updated for an expired lease."""
    expired_house = Mock(spec=House)
    expired_house.id = 1
    expired_house.vn_house_lease_end_date = date.today() - timedelta(days=1)

    mock_house_repository.model.query.get.return_value = expired_house

    with patch("src.core.services.house_service.db") as mock_db:
        house_service.update_lease_end_date_if_expired(house_id=1)

        # Check that the date was updated and session was committed
        assert expired_house.vn_house_lease_end_date == date.today() + timedelta(
            days=29
        )
        mock_db.session.commit.assert_called_once()


def test_get_status_label(app_context, house_service, mock_house_repository):
    """Test the get_status_label method for different house statuses."""
    open_house = Mock(spec=House, vn_house_is_open=True)
    closed_house = Mock(spec=House, vn_house_is_open=False)

    mock_house_repository.model.query.get.side_effect = [open_house, closed_house, None]

    assert house_service.get_status_label(house_id=1) == "Occupée"
    assert house_service.get_status_label(house_id=2) == "Libre"
    assert house_service.get_status_label(house_id=3) == "N/A"


def test_get_current_tenant_id(app_context, house_service, mock_tenant_repository):
    """Test retrieving the ID of the current tenant for a house."""
    tenant = Mock(spec=Tenant, id=101)
    mock_tenant_repository.find_by_house_id.return_value = tenant

    tenant_id = house_service.get_current_tenant_id(house_id=1)
    assert tenant_id == 101


def test_get_current_tenant_id_no_tenant(
    app_context, house_service, mock_tenant_repository
):
    """Test get_current_tenant_id when no tenant is found."""
    mock_tenant_repository.find_by_house_id.return_value = None

    tenant_id = house_service.get_current_tenant_id(house_id=1)
    assert tenant_id is None
