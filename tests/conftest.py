import pytest
from src.main import create_app


@pytest.fixture(scope="function")
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    app = create_app("test")
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture(scope="function")
def app_context(app):
    """Yields an application context for the tests."""
    with app.app_context():
        yield
