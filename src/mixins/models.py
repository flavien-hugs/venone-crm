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


class DefaultUserInfoModel(Updateable):

    __abstract__ = True

    vn_gender = db.Column(db.String(4), name="gender", nullable=False)
    vn_fullname = db.Column(db.String(80), name="name & surname", nullable=False)
    vn_addr_email = db.Column(db.String(80), unique=True, nullable=False)
    vn_profession = db.Column(db.String(100), name="profession", nullable=True)
    vn_parent_name = db.Column(db.String(80), name="parent's name", nullable=True)
    vn_phonenumber_one = db.Column(db.String(20), unique=True, nullable=True)
    vn_phonenumber_two = db.Column(db.String(20), unique=True, nullable=True)
    vn_cni_number = db.Column(
        db.String(11), name="national ID card number", unique=True, nullable=True
    )
    vn_location = db.Column(db.String(180), name="location of residence", nullable=True)
    vn_activated = db.Column(db.Boolean, name="status", nullable=False, default=True)
