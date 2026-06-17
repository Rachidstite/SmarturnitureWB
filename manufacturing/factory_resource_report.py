from dataclasses import dataclass


@dataclass
class FactoryResourceReport:
    workers: int = 0
    cnc_machines: int = 0
    edge_banding_machines: int = 0
    assembly_stations: int = 0
    daily_work_hours: float = 0.0
    workdays_per_week: int = 0
    weekly_capacity_hours: float = 0.0
