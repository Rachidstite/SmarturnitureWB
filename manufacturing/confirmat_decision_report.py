from dataclasses import dataclass


@dataclass
class ConfirmatDecisionReport:
    decision_status: str = ""
    is_manufacturable: bool = False
    is_blocked: bool = False
    requires_review: bool = False
    blocking_reason: str = ""
    warning_reason: str = ""
    recommended_fix: str = ""
    factory_visibility_message: str = ""
