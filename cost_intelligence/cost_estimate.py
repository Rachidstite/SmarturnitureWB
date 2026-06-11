from dataclasses import dataclass, field


@dataclass
class CostEstimate:
    """
    Cost Intelligence V1 result contract.

    Represents actual production cost summary.
    It does not represent engineering remediation cost,
    optimization savings, or customer quotation price.
    """

    material_cost: float = 0.0

    sheet_cost: float = 0.0

    waste_cost: float = 0.0

    hardware_cost: float = 0.0

    edge_banding_cost: float = 0.0

    machining_cost: float = 0.0

    labor_cost: float = 0.0

    total_cost: float = 0.0

    currency: str = "MAD"

    warnings: list = field(
        default_factory=list
    )
