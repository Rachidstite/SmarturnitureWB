from dataclasses import dataclass


@dataclass
class ManufacturingIntelligenceReport:

    errors: list

    warnings: list

    recommendations: list

    optimizations: list

    can_export: bool
