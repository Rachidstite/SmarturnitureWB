from dataclasses import dataclass, field
from typing import Any


@dataclass
class ManufacturingQuotationInput:
    manufacturing_cost_summary: Any = None
    base_cost: float = 0.0
    markup_rate: float = 0.0
    currency: str = "MAD"
    warnings: list = field(default_factory=list)
