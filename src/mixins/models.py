import uuid
from datetime import datetime


from .. import db
from ..utils import Updateable
from sqlalchemy_utils import UUIDType, IPAddressType


class TimestampMixin(Updateable, db.Model):

    __abstract__ = True

    id = db.Column(
        UUIDType(binary=False), index=True,
        primary_key=True, default=uuid.uuid4
    )
    vn_created_at = db.Column(db.DateTime, default=datetime.utcnow())
    vn_updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())
