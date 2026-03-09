from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserEntity:
    id: int
    uuid: str
    fullname: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    country: Optional[str]  # Optional: can be NULL in DB
    balance: float
    is_house_owner: bool
    is_company: bool
    is_administrator: bool = False
    owner_percent: float = 7.0
    company_percent: float = 6.0

    def get_display_name(self) -> str:
        return self.fullname or self.email or "Utilisateur"
