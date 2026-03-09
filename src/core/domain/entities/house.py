from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class HouseEntity:
    id: int
    uuid: str  # The internal numeric-like string or id_generator result
    type: str  # Maison, Appartement...
    rent: float
    is_open: bool  # True if occupied/unavailable?
    lease_end_date: Optional[date]
    user_id: Optional[int]
    owner_id: Optional[int]

    def is_available(self) -> bool:
        return not self.is_open

    def get_status_label(self) -> str:
        return "indisponible" if self.is_open else "disponible"
