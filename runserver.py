import logging as lg

import click
from flask_migrate import upgrade

from src.auth.models import VNPercent, VNRole, VNUser
from src.exts import db
from src.payment.models import VNPayment, VNTransferRequest
from src.tenant.models import VNHouse, VNHouseOwner, VNTenant
from src.venone import venone_app


@venone_app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        users=VNUser,
        percents=VNPercent,
        tenants=VNTenant,
        houses=VNHouse,
        houseowners=VNHouseOwner,
        payments=VNPayment,
        transfers=VNTransferRequest,
    )


@venone_app.cli.command("init-db")
def init_db():
    try:
        lg.info("Running migrations...")
        upgrade()
        lg.info("Migrations complete. Syncing roles...")
        VNRole.insert_roles()
        db.session.commit()
        lg.info("Database initialized successfully!")
    except Exception as e:
        lg.error(f"Failed to initialize database: {e}")
        db.session.rollback()
        raise e


@venone_app.cli.command("init-roles")
def init_roles():
    VNRole.insert_roles()
    db.session.commit()
    lg.info("Roles initialized !")


@venone_app.cli.command("create-admin")
def create_admin():
    VNUser.create_admin()


@venone_app.cli.command("drop-db")
def drop_db():
    try:
        db.drop_all()
        # Ensure alembic_version is also dropped to allow fresh migrations
        db.session.execute(db.text("DROP TABLE IF EXISTS alembic_version;"))
        db.session.commit()
        lg.info("Database dropped and migration history cleared !")
    except Exception as e:
        lg.error(f"Error dropping database: {e}")
        db.session.rollback()
        raise e


@venone_app.cli.command("seed-db")
@click.option("--count", default=5, help="Number of items to seed.")
def seed_db(count):
    from src.seeder import SeedManager

    seeder = SeedManager(count=count)
    seeder.run()


if __name__ == "__main__":
    venone_app.run()
