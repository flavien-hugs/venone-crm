from src.core.repositories.base_repository import BaseRepository
from src.infrastructure.persistence.models import Tenant


class TenantRepository(BaseRepository):
    model = Tenant

    def find_by_tenant_id(self, vn_tenant_id: str):
        return self.model.query.filter_by(vn_tenant_id=vn_tenant_id).first()

    def find_by_user_id(self, user_id: int):
        return self.model.query.filter_by(vn_user_id=user_id).all()

    def find_by_house_id(self, house_id: int):
        return self.model.query.filter_by(vn_house_id=house_id).order_by(self.model.vn_created_at.desc()).first()
