from dataclasses import dataclass


@dataclass
class FactoryGovernanceCommercialImpactReport:
    estimated_margin_improvement: float = 0.0
    estimated_cost_reduction: float = 0.0
    estimated_profit_increase: float = 0.0
    impact_confidence: float = 0.0
    impact_explanation: str = ""
