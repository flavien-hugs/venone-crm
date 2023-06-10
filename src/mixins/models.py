import secrets
import uuid
from datetime import datetime

from src.exts import db


def id_generator():
    return secrets.randbelow(100000)


class CRUDMixin(object):

    __table_args__ = {"extend_existing": True}

    id = db.Column(
        db.Integer,
        unique=True,
        index=True,
        nullable=False,
        primary_key=True,
    )

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, str) and id.isdigit(), isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
        return self.save()

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def remove(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def disable(self):
        self.vn_activated = False
        db.session.add(self)
        db.session.commit()


class TimestampMixin(CRUDMixin, db.Model):

    __abstract__ = True

    uuid = db.Column(db.String(40), index=True, default=lambda: str(uuid.uuid4()))
    vn_created_at = db.Column(db.DateTime, default=datetime.utcnow())
    vn_updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())

    @classmethod
    def find_by_uuid(cls, uuid):
        return cls.query.filter_by(uuid=uuid).first()


class DefaultUserInfoModel(db.Model):

    __abstract__ = True

    vn_gender = db.Column(db.String(10), nullable=True)
    vn_fullname = db.Column(db.String(80), nullable=False)
    vn_addr_email = db.Column(db.String(80), unique=True, nullable=False)
    vn_profession = db.Column(db.String(100), nullable=True)
    vn_parent_name = db.Column(db.String(80), nullable=True)
    vn_phonenumber_one = db.Column(db.String(20), unique=True, nullable=False)
    vn_phonenumber_two = db.Column(db.String(20), nullable=True)
    vn_cni_number = db.Column(db.String(80), nullable=True)
    vn_location = db.Column(db.String(180), nullable=True)
    vn_activated = db.Column(db.Boolean, default=True)

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(vn_addr_email=email).first()

    @classmethod
    def find_by_email_and_phone(cls, obj):
        return cls.query.filter(
            (cls.vn_addr_email == obj) | (cls.vn_phonenumber_one == obj)
        ).first()
