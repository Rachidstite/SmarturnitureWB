from dataclasses import dataclass


@dataclass
class ManufacturingIntelligenceReport:

    errors: list

    warnings: list

    structural_warnings: list

    recommendations: list

    optimizations: list

    cost_impacts: list

    score: object = None

    can_export: bool = True
