from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OwnerEntity:
    id: int
    uuid: str  # From id_generator
    fullname: str
    phone: str
    owner_percent: float  # 7% ?
    user_id: Optional[int]


@dataclass(frozen=True)
class TenantEntity:
    id: int
    uuid: str  # From id_generator
    fullname: str
    phone: str
    user_id: Optional[int]
