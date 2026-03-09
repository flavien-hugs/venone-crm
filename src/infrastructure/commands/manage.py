import logging

import click
from flask_migrate import upgrade
from src.infrastructure.config.plugins import db
from src.infrastructure.persistence.models import (
    House,
    HouseOwner,
    Payment,
    Percent,
    Role,
    Tenant,
    TransferRequest,
    User,
)

logger = logging.getLogger(__name__)


def register_commands(app):
    """
    Registers all custom CLI commands to the app instance.
    This follows SRP by separating command definitions from the main entry point.
    """

    @app.shell_context_processor
    def make_shell_context():
        """Shell context for debugging - automatically imports all models."""
        return dict(
            db=db,
            User=User,
            Percent=Percent,
            Tenant=Tenant,
            House=House,
            HouseOwner=HouseOwner,
            Payment=Payment,
            TransferRequest=TransferRequest,
            Role=Role,
        )

    @app.cli.command("init-db")
    def init_db():
        """Initialize database: run migrations and insert essential roles."""
        try:
            logger.info("Starting database initialization...")
            upgrade()
            logger.info("Database schema upgraded. Syncing roles...")
            Role.insert_roles()
            db.session.commit()
            logger.info("Database initialized successfully!")
        except Exception as e:
            logger.exception(f"Critical failure during database initialization: {e}")
            db.session.rollback()
            raise e

    @app.cli.command("init-roles")
    def init_roles():
        """Sync predefined roles from the model logic."""
        try:
            Role.insert_roles()
            db.session.commit()
            logger.info("Roles synchronized successfully.")
        except Exception as e:
            logger.exception(f"Error initializing roles: {e}")
            db.session.rollback()

    @app.cli.command("create-admin")
    def create_admin():
        """Create the super-admin user based on environment variables."""
        try:
            User.create_admin()
            logger.info("Admin creation process completed.")
        except Exception as e:
            logger.exception(f"Error creating admin: {e}")

    @app.cli.command("drop-db")
    @click.confirmation_option(prompt="Are you sure you want to drop all data?")
    def drop_db():
        """Dangerous: Drops all tables and migration history."""
        try:
            db.drop_all()
            # Special handling for Alembic table to allow re-initialization
            db.session.execute(db.text("DROP TABLE IF EXISTS alembic_version;"))
            db.session.commit()
            logger.info("Database cleared and migration history deleted.")
        except Exception as e:
            logger.error(f"Error dropping database: {e}")
            db.session.rollback()
            raise e

    @app.cli.command("seed-db")
    @click.option("--count", default=5, type=int, help="Number of items to seed.")
    def seed_db(count):
        """Populate database with development data."""
        try:
            from src.infrastructure.persistence.seeders import SeedManager

            logger.info(f"Seeding database with {count} entries...")
            seeder = SeedManager(count=count)
            seeder.run()
            logger.info("Seeding process completed successfully.")
        except Exception as e:
            logger.exception(f"Seeding failed: {e}")
