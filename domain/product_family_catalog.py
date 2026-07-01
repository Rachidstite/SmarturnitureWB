from __future__ import annotations

from domain.product_family import ProductFamily
from domain.product_family_registry import ProductFamilyRegistry


BASE_CABINET = ProductFamily(
    family_id="BASE_CABINET",
    name="Base Cabinet",
    category="kitchen",
    description="Standard floor-mounted cabinet family.",
    default_parameters={
        "width_mm": 600.0,
        "height_mm": 720.0,
        "depth_mm": 580.0,
    },
    engineering_defaults={
        "door_count": 2,
        "shelf_count": 1,
        "has_back_panel": True,
    },
    manufacturing_defaults={
        "edge_banding_required": True,
        "toe_kick_required": True,
    },
    visual_defaults={
        "supports_overlay_preview": True,
        "default_finish": "MDF_18MM",
    },
    commercial_defaults={
        "pricing_group": "STANDARD_BASE",
    },
    metadata={
        "release_status": "foundation",
    },
)

WALL_CABINET = ProductFamily(
    family_id="WALL_CABINET",
    name="Wall Cabinet",
    category="kitchen",
    description="Suspended cabinet family for wall-mounted storage.",
    default_parameters={
        "width_mm": 600.0,
        "height_mm": 720.0,
        "depth_mm": 350.0,
    },
    engineering_defaults={
        "door_count": 2,
        "shelf_count": 2,
        "has_back_panel": True,
    },
    manufacturing_defaults={
        "edge_banding_required": True,
        "toe_kick_required": False,
    },
    visual_defaults={
        "supports_overlay_preview": True,
        "default_finish": "MDF_18MM",
    },
    commercial_defaults={
        "pricing_group": "STANDARD_WALL",
    },
    metadata={
        "mounting_type": "wall",
        "release_status": "foundation",
    },
)

TALL_CABINET = ProductFamily(
    family_id="TALL_CABINET",
    name="Tall Cabinet",
    category="kitchen",
    description="Full-height storage cabinet family.",
    default_parameters={
        "width_mm": 600.0,
        "height_mm": 2100.0,
        "depth_mm": 580.0,
    },
    engineering_defaults={
        "door_count": 2,
        "shelf_count": 4,
        "has_back_panel": True,
    },
    manufacturing_defaults={
        "edge_banding_required": True,
        "toe_kick_required": True,
    },
    visual_defaults={
        "supports_overlay_preview": True,
        "default_finish": "MDF_18MM",
    },
    commercial_defaults={
        "pricing_group": "STANDARD_TALL",
    },
    metadata={
        "storage_type": "full_height",
        "release_status": "foundation",
    },
)

BUILT_IN_PRODUCT_FAMILY_REGISTRY = (
    ProductFamilyRegistry()
    .with_family(BASE_CABINET)
    .with_family(WALL_CABINET)
    .with_family(TALL_CABINET)
)
