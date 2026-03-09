from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional


@dataclass(frozen=True)
class PaymentEntity:
    id: int
    transaction_id: str
    amount: float
    status: bool  # Paid?
    date: date
    house_id: int
    tenant_id: int
    payee_id: int
    metadata: Optional[Dict] = None

    def is_confirmed(self) -> bool:
        return self.status
