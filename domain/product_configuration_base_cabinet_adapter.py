from __future__ import annotations

from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration


_SUPPORTED_FAMILY_IDS = {"BASE_CABINET", "base_cabinet"}
_OPTION_FIELDS = (
    "door_count",
    "shelf_count",
    "has_back_panel",
    "edge_banding_required",
    "toe_kick_required",
    "hinge_family",
    "drawer_family",
)


def adapt_product_configuration_to_base_cabinet_specification(
    configuration: ProductConfiguration,
) -> BaseCabinetSpecification:
    if configuration.family_id not in _SUPPORTED_FAMILY_IDS:
        raise ValueError(
            "Unsupported family_id for BaseCabinetSpecification adapter: "
            f"{configuration.family_id}"
        )

    specification_kwargs = {
        "width_mm": configuration.width,
        "height_mm": configuration.height,
        "depth_mm": configuration.depth,
    }

    options = dict(configuration.options or {})
    for option_name in _OPTION_FIELDS:
        if option_name in options:
            specification_kwargs[option_name] = options[option_name]

    return BaseCabinetSpecification(**specification_kwargs)
