from dataclasses import dataclass


@dataclass
class ManufacturingSimulationReport:
    panel_count: int = 0
    machining_operation_count: int = 0
    edge_operation_count: int = 0
    drilling_operation_count: int = 0
    assembly_operation_count: int = 0
    estimated_cnc_minutes: float = 0.0
    estimated_edge_banding_minutes: float = 0.0
    estimated_assembly_minutes: float = 0.0
    estimated_total_factory_minutes: float = 0.0
    simulation_status: str = "READY"
    simulation_recommendation: str = ""
