from dataclasses import dataclass


@dataclass
class ShelfStructuralReport:
    span_risk: str = "LOW"
    sagging_risk: str = "LOW"
    support_required: bool = False
    shelf_recommendation: str = ""
