import pytest
from unittest.mock import Mock

from src.core.mappers.stakeholders_mapper import OwnerMapper, TenantMapper
from src.core.domain.entities.stakeholders import OwnerEntity, TenantEntity
from src.infrastructure.persistence.models import HouseOwner, Tenant

@pytest.fixture
def mock_persistence_owner():
    """Fixture for a mock SQLAlchemy HouseOwner model instance."""
    mock_owner = Mock(spec=HouseOwner)
    mock_owner.id = 1
    mock_owner.vn_owner_id = "OWN123"
    mock_owner.vn_fullname = "Owner Name"
    mock_owner.vn_phonenumber_one = "111222333"
    mock_owner.vn_owner_percent = 12.5
    mock_owner.vn_user_id = 10
    return mock_owner

@pytest.fixture
def mock_persistence_tenant():
    """Fixture for a mock SQLAlchemy Tenant model instance."""
    mock_tenant = Mock(spec=Tenant)
    mock_tenant.id = 2
    mock_tenant.vn_tenant_id = "TEN456"
    mock_tenant.vn_fullname = "Tenant Name"
    mock_tenant.vn_phonenumber_one = "444555666"
    mock_tenant.vn_user_id = 11
    mock_tenant.vn_house_id = 22
    return mock_tenant

def test_owner_to_domain_conversion(app_context, mock_persistence_owner):
    """Test that OwnerMapper correctly converts a persistence model to a domain entity."""
    domain_entity = OwnerMapper.to_domain(mock_persistence_owner)

    assert isinstance(domain_entity, OwnerEntity)
    assert domain_entity.id == mock_persistence_owner.id
    assert domain_entity.uuid == mock_persistence_owner.vn_owner_id
    assert domain_entity.fullname == mock_persistence_owner.vn_fullname
    assert domain_entity.phone == mock_persistence_owner.vn_phonenumber_one
    assert domain_entity.owner_percent == mock_persistence_owner.vn_owner_percent
    assert domain_entity.user_id == mock_persistence_owner.vn_user_id

def test_tenant_to_domain_conversion(app_context, mock_persistence_tenant):
    """Test that TenantMapper correctly converts a persistence model to a domain entity."""
    domain_entity = TenantMapper.to_domain(mock_persistence_tenant)

    assert isinstance(domain_entity, TenantEntity)
    assert domain_entity.id == mock_persistence_tenant.id
    assert domain_entity.uuid == mock_persistence_tenant.vn_tenant_id
    assert domain_entity.fullname == mock_persistence_tenant.vn_fullname
    assert domain_entity.phone == mock_persistence_tenant.vn_phonenumber_one
    assert domain_entity.user_id == mock_persistence_tenant.vn_user_id
