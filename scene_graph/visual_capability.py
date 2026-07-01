from dataclasses import dataclass


@dataclass
class VisualCapability:
    supports_edge_visualization: bool = False
    supports_drill_visualization: bool = False
    supports_groove_visualization: bool = False
    supports_hardware_visualization: bool = False
    supports_material_visualization: bool = False
    supports_dimension_visualization: bool = False
