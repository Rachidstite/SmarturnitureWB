from dataclasses import dataclass


@dataclass
class CapacityReservationDecisionReport:
    decision_status: str = ""
    is_manufacturable: bool = False
    is_blocked: bool = False
    requires_review: bool = False
    blocking_reason: str = ""
    warning_reason: str = ""
    recommended_fix: str = ""
    capacity_reservation_action: str = ""
    factory_visibility_message: str = ""
