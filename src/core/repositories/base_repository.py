from src.core.interfaces.repository import IRepository
from src.infrastructure.config.plugins import db


class BaseRepository(IRepository):
    model = None
    mapper = None

    def get_by_id(self, id: int):
        record = db.session.get(self.model, id)
        if record and self.mapper:
            return self.mapper.to_domain(record)
        return record

    def find_all(self):
        records = self.model.query.all()
        if self.mapper:
            return [self.mapper.to_domain(r) for r in records]
        return records

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        return instance

    def update(self, id: int, **kwargs):
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db.session.add(instance)
        return instance

    def delete(self, id: int):
        instance = self.get_by_id(id)
        if instance:
            db.session.delete(instance)
        return instance

    def commit(self):
        db.session.commit()
