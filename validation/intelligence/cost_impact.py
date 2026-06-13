from dataclasses import dataclass


@dataclass
class CostImpact:

    category: str

    estimated_savings: float

    description: str
