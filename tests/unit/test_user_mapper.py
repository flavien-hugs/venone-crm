import pytest
from unittest.mock import Mock

from src.core.mappers.user_mapper import UserMapper
from src.core.domain.entities.user import UserEntity
from src.infrastructure.persistence.models import User, Role, Permission


@pytest.fixture
def mock_persistence_user():
    """Fixture for a mock SQLAlchemy User model instance."""
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.uuid = "test-uuid-123"
    mock_user.vn_fullname = "John Doe"
    mock_user.vn_addr_email = "john.doe@example.com"
    mock_user.vn_phonenumber_one = "123456789"
    mock_user.vn_country = "SN"
    mock_user.vn_balance = 1000.50
    mock_user.vn_house_owner = True
    mock_user.vn_company = False

    # Mock the role and its methods
    mock_role = Mock(spec=Role)
    mock_role.has_permission.side_effect = lambda perm: perm == Permission.ADMIN
    mock_user.role = mock_role
    mock_user.is_administrator.return_value = mock_role.has_permission(Permission.ADMIN)

    # Mock percent relationship
    mock_percent = Mock()
    mock_percent.vn_owner_percent = 8.0
    mock_percent.vn_company_percent = 5.0
    mock_user.percent = mock_percent

    mock_user.get_owner_percent.return_value = mock_percent.vn_owner_percent
    mock_user.get_company_percent.return_value = mock_percent.vn_company_percent

    return mock_user


@pytest.fixture
def mock_domain_user():
    """Fixture for a mock UserEntity domain instance."""
    return UserEntity(
        id=2,
        uuid="test-uuid-456",
        fullname="Jane Smith",
        email="jane.smith@example.com",
        phone="987654321",
        country="TG",
        balance=2000.75,
        is_house_owner=False,
        is_company=True,
        is_administrator=False,
        owner_percent=7.0,
        company_percent=6.0,
    )


def test_to_domain_conversion(app_context, mock_persistence_user):
    """Test that UserMapper correctly converts a persistence model to a domain entity."""
    domain_entity = UserMapper.to_domain(mock_persistence_user)

    assert domain_entity.id == mock_persistence_user.id
    assert domain_entity.uuid == mock_persistence_user.uuid
    assert domain_entity.fullname == mock_persistence_user.vn_fullname
    assert domain_entity.email == mock_persistence_user.vn_addr_email
    assert domain_entity.phone == mock_persistence_user.vn_phonenumber_one
    assert domain_entity.country == mock_persistence_user.vn_country
    assert domain_entity.balance == mock_persistence_user.vn_balance
    assert domain_entity.is_house_owner == mock_persistence_user.vn_house_owner
    assert domain_entity.is_company == mock_persistence_user.vn_company
    assert domain_entity.is_administrator == mock_persistence_user.is_administrator()
    assert domain_entity.owner_percent == mock_persistence_user.get_owner_percent()
    assert domain_entity.company_percent == mock_persistence_user.get_company_percent()


def test_to_persistence_conversion(app_context, mock_domain_user):
    """Test that UserMapper correctly converts a domain entity to a persistence dictionary."""
    persistence_dict = UserMapper.to_persistence(mock_domain_user)

    assert persistence_dict["vn_fullname"] == mock_domain_user.fullname
    assert persistence_dict["vn_addr_email"] == mock_domain_user.email
    assert persistence_dict["vn_phonenumber_one"] == mock_domain_user.phone
    assert persistence_dict["vn_country"] == mock_domain_user.country
    assert persistence_dict["vn_balance"] == mock_domain_user.balance
    assert persistence_dict["vn_house_owner"] == mock_domain_user.is_house_owner
    assert persistence_dict["vn_company"] == mock_domain_user.is_company


def test_to_domain_with_none_values(app_context):
    """Test to_domain with persistence user having None for optional fields."""
    mock_user = Mock(spec=User)
    mock_user.id = 3
    mock_user.uuid = None
    mock_user.vn_fullname = None
    mock_user.vn_addr_email = None
    mock_user.vn_phonenumber_one = None
    mock_user.vn_country = None
    mock_user.vn_balance = None
    mock_user.vn_house_owner = None
    mock_user.vn_company = None

    mock_role = Mock(spec=Role)
    mock_role.has_permission.return_value = False
    mock_user.role = mock_role
    mock_user.is_administrator.return_value = False

    mock_percent = Mock()
    mock_percent.vn_owner_percent = None
    mock_percent.vn_company_percent = None
    mock_user.percent = mock_percent

    mock_user.get_owner_percent.return_value = 7.0  # Default if None
    mock_user.get_company_percent.return_value = 6.0  # Default if None

    domain_entity = UserMapper.to_domain(mock_user)

    assert domain_entity.uuid == ""
    assert domain_entity.fullname is None
    assert domain_entity.email is None
    assert domain_entity.phone is None
    assert domain_entity.country is None
    assert domain_entity.balance == 0.0
    assert domain_entity.is_house_owner is False
    assert domain_entity.is_company is False
    assert domain_entity.is_administrator is False
    assert domain_entity.owner_percent == 7.0
    assert domain_entity.company_percent == 6.0
