from dataclasses import dataclass, field


@dataclass
class CostPackageReport:
    """Summary of cost-relevant evidence available from a FactoryReleasePackage.

    Fields that cannot be priced at this layer (because the underlying cost
    engine requires ``ManufacturingProductionPackage`` context) are set to
    ``0.0`` and documented in ``warnings`` — no invented values.
    """

    material_cost_total: float = 0.0
    hardware_cost_total: float = 0.0
    machining_cost_total: float = 0.0
    assembly_cost_total: float = 0.0
    total_cost: float = 0.0
    warnings: list = field(default_factory=list)
    source: str = ""
