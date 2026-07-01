from __future__ import annotations

from domain.wall_cabinet_specification import WallCabinetSpecification
from domain.product_configuration import ProductConfiguration


def build_wall_cabinet_specification_from_product_configuration(
    product_configuration: ProductConfiguration,
) -> WallCabinetSpecification:
    defaults = WallCabinetSpecification()
    wall_options = dict(product_configuration.options or {})

    return WallCabinetSpecification(
        width_mm=product_configuration.width,
        height_mm=product_configuration.height,
        depth_mm=product_configuration.depth,
        door_count=int(wall_options.get("door_count", defaults.door_count)),
        shelf_count=int(wall_options.get("shelf_count", defaults.shelf_count)),
        has_back_panel=bool(
            wall_options.get("has_back_panel", defaults.has_back_panel)
        ),
        edge_banding_required=bool(
            wall_options.get("edge_banding_required", defaults.edge_banding_required)
        ),
        hinge_family=str(wall_options.get("hinge_family", defaults.hinge_family)),
        suspension_hardware_family=str(
            wall_options.get(
                "suspension_hardware_family",
                defaults.suspension_hardware_family,
            )
        ),
        wall_type=str(wall_options.get("wall_type", defaults.wall_type)),
        max_load_kg=float(wall_options.get("max_load_kg", defaults.max_load_kg)),
        required_clearance_mm=float(
            wall_options.get("required_clearance_mm", defaults.required_clearance_mm)
        ),
    )
