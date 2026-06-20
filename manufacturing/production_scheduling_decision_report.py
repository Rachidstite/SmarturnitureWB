from dataclasses import dataclass


@dataclass
class ProductionSchedulingDecisionReport:
    decision_status: str = ""
    is_manufacturable: bool = False
    is_blocked: bool = False
    requires_review: bool = False
    blocking_reason: str = ""
    warning_reason: str = ""
    recommended_fix: str = ""
    production_schedule_action: str = ""
    factory_visibility_message: str = ""
