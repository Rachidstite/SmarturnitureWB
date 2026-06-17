from dataclasses import dataclass, field


@dataclass
class JoineryCostIntelligenceReport:
    total_joinery_cost: float = 0.0
    minifix_cost: float = 0.0
    hinge_cost: float = 0.0
    drawer_slide_cost: float = 0.0
    handle_cost: float = 0.0
    cost_breakdown: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
