from datetime import datetime

from .. import db
from ..mixins.models import TimestampMixin, DefaultUserInfoModel


class VNTenant(DefaultUserInfoModel, db.Model):

    __tablename__ = "tenant"

    vn_avatar = db.Column(db.String(80), name="tenant avatar", nullable=True)
    vn_activated = db.Column(db.Boolean, name="tenant status", nullable=False, default=False)
    vn_birthdate = db.Column(db.Date, name="tenant birth date", nullable=True)
    vn_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.vn_fullname

    def __repr__(self):
        return "<VNTenant %r>" % self.vn_fullname
