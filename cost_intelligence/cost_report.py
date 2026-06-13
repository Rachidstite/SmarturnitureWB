from dataclasses import dataclass, field


@dataclass
class CostReport:
    """
    Commercial-facing production cost report.

    This does not represent a customer quotation price.
    """

    material_cost: float = 0.0

    sheet_cost: float = 0.0

    waste_cost: float = 0.0

    hardware_cost: float = 0.0

    total_cost: float = 0.0

    currency: str = "MAD"

    warnings: list = field(
        default_factory=list
    )

    @classmethod
    def from_estimate(
        cls,
        estimate,
    ):
        return cls(
            material_cost=estimate.material_cost,
            sheet_cost=estimate.sheet_cost,
            waste_cost=estimate.waste_cost,
            hardware_cost=estimate.hardware_cost,
            total_cost=estimate.total_cost,
            currency=estimate.currency,
            warnings=list(estimate.warnings),
        )
