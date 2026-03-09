import pytest
from unittest.mock import Mock
from datetime import date

from src.core.mappers.house_mapper import HouseMapper
from src.core.domain.entities.house import HouseEntity
from src.infrastructure.persistence.models import House


@pytest.fixture
def mock_persistence_house():
    """Fixture for a mock SQLAlchemy House model instance."""
    mock_house = Mock(spec=House)
    mock_house.id = 1
    mock_house.vn_house_id = "H123"
    mock_house.vn_house_type = "Appartement"
    mock_house.vn_house_rent = 150000.0
    mock_house.vn_house_is_open = False
    mock_house.vn_house_lease_end_date = date(2024, 12, 31)
    mock_house.vn_user_id = 10
    mock_house.vn_owner_id = 20
    return mock_house


@pytest.fixture
def mock_domain_house():
    """Fixture for a mock HouseEntity domain instance."""
    return HouseEntity(
        id=2,
        uuid="H456",
        type="Villa",
        rent=500000.0,
        is_open=True,
        lease_end_date=date(2025, 1, 1),
        user_id=11,
        owner_id=21,
    )


def test_to_domain_conversion(app_context, mock_persistence_house):
    """Test that HouseMapper correctly converts a persistence model to a domain entity."""
    domain_entity = HouseMapper.to_domain(mock_persistence_house)

    assert isinstance(domain_entity, HouseEntity)
    assert domain_entity.id == mock_persistence_house.id
    assert domain_entity.uuid == mock_persistence_house.vn_house_id
    assert domain_entity.type == mock_persistence_house.vn_house_type
    assert domain_entity.rent == mock_persistence_house.vn_house_rent
    assert domain_entity.is_open == mock_persistence_house.vn_house_is_open
    assert (
        domain_entity.lease_end_date == mock_persistence_house.vn_house_lease_end_date
    )
    assert domain_entity.user_id == mock_persistence_house.vn_user_id
    assert domain_entity.owner_id == mock_persistence_house.vn_owner_id


def test_to_persistence_conversion(app_context, mock_domain_house):
    """Test that HouseMapper correctly converts a domain entity to a persistence dictionary."""
    persistence_dict = HouseMapper.to_persistence(mock_domain_house)

    assert persistence_dict["vn_house_type"] == mock_domain_house.type
    assert persistence_dict["vn_house_rent"] == mock_domain_house.rent
    assert persistence_dict["vn_house_is_open"] == mock_domain_house.is_open
    assert (
        persistence_dict["vn_house_lease_end_date"] == mock_domain_house.lease_end_date
    )
    assert persistence_dict["vn_user_id"] == mock_domain_house.user_id
    assert persistence_dict["vn_owner_id"] == mock_domain_house.owner_id
