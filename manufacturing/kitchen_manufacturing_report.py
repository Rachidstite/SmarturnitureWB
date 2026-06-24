from dataclasses import dataclass


@dataclass
class KitchenManufacturingReport:
    cabinet_count: int = 0
    drawer_count: int = 0
    door_count: int = 0
    manufacturing_complexity: str = "LOW"
    requires_engineering_review: bool = False
    manufacturing_recommendation: str = ""
