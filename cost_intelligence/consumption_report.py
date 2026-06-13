from dataclasses import dataclass, field


@dataclass
class ConsumptionReport:
    """
    Manufacturing consumption output contract.
    """

    material_consumption: float = 0.0

    sheet_consumption: float = 0.0

    hardware_consumption: float = 0.0

    waste_ratio: float = 0.0

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
            material_consumption=getattr(
                estimate,
                "material_consumption",
                0.0,
            ),
            sheet_consumption=getattr(
                estimate,
                "sheet_consumption",
                0.0,
            ),
            hardware_consumption=getattr(
                estimate,
                "hardware_consumption",
                0.0,
            ),
            waste_ratio=getattr(
                estimate,
                "waste_ratio",
                0.0,
            ),
            currency=estimate.currency,
            warnings=list(estimate.warnings),
        )
