from dataclasses import dataclass


@dataclass
class FurnitureProjectSummary:
    total_cabinets: int = 0
    total_physical_parts: int = 0
    total_machining_operations: int = 0
