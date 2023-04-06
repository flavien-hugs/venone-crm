import logging as lg

from flask_migrate import Migrate
from flask_migrate import upgrade
from src import db
from src.auth.models import VNRole
from src.auth.models import VNUser
from src.payment.models import VNPayment
from src.tenant.models import VNHouse
from src.tenant.models import VNHouseOwner
from src.tenant.models import VNTenant

from src.venone import venone_app

migrate = Migrate(venone_app, db, render_as_batch=True)


@venone_app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        user=VNUser,
        tenant=VNTenant,
        house=VNHouse,
        houseowner=VNHouseOwner,
        payment=VNPayment,
    )


@venone_app.cli.command("init_db")
def init_db():
    upgrade()
    db.create_all()
    VNRole.insert_roles()
    db.session.commit()
    lg.warning("Database initialized !")


if __name__ == "__main__":
    venone_app.run()
