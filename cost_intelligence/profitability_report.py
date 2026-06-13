from dataclasses import dataclass, field


@dataclass
class ProfitabilityReport:
    """
    Profitability output contract.
    """

    production_cost: float = 0.0

    selling_price: float = 0.0

    gross_profit: float = 0.0

    gross_margin_rate: float = 0.0

    currency: str = "MAD"

    warnings: list = field(
        default_factory=list
    )
