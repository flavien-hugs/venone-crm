import uuid
from datetime import datetime

from .. import db
from ..utils import Updateable


class TimestampMixin(Updateable, db.Model):

    __abstract__ = True

    id = db.Column(
        db.Integer,
        unique=True,
        index=True,
        nullable=False,
        primary_key=True,
    )
    uuid = db.Column(db.String(40), name="uuid", index=True, default=str(uuid.uuid4()))
    vn_created_at = db.Column(db.DateTime, default=datetime.utcnow())
    vn_updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())
