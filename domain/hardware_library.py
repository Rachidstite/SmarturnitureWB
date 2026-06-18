from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path
from domain.anchors import MountFace
from domain.hardware_catalog_loader import HardwareCatalogLoader

@dataclass
class HoleSpec:
    diameter: float
    depth: float
    face: MountFace = MountFace.FRONT
    axis: str = "Z"                   # CNC Machining Axis
    offset_x: float = 0.0
    offset_y: float = 0.0
    is_through_hole: bool = False

@dataclass
class HardwareSpec:
    sku: str
    manufacturer: str
    model: str
    revision: str
    category: str
    price: float = 0.0
    host_holes: List[HoleSpec] = field(default_factory=list)
    target_holes: List[HoleSpec] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        """The single source of truth for UI and BOM naming"""
        return f"{self.manufacturer} {self.model}"

class HardwareRegistry:
    def __init__(self):
        self._catalog: Dict[str, HardwareSpec] = {}
        self._seed_catalog()
        self._catalog.update(
            HardwareCatalogLoader.load(
                Path(__file__).resolve().parent.parent
                / "data"
                / "hardware"
                / "drawer_slides.json"
            )
        )

    def get_hardware(self, sku: str) -> HardwareSpec:
        return self._catalog.get(sku)

    def _seed_catalog(self):
        self._catalog["HINGE_BLUM_110_V1"] = HardwareSpec(
            sku="HINGE_BLUM_110_V1", manufacturer="BLUM", model="CLIP_TOP_110", revision="1.0", category="HINGES", price=6.0,
            host_holes=[
                HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, offset_x=37, offset_y=16),
                HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, offset_x=37, offset_y=-16)
            ],
            target_holes=[
                HoleSpec(diameter=35, depth=12.5, face=MountFace.BACK, offset_x=22, offset_y=0),
                HoleSpec(diameter=2.5, depth=10, face=MountFace.BACK, offset_x=22-9.5, offset_y=22.5),
                HoleSpec(diameter=2.5, depth=10, face=MountFace.BACK, offset_x=22-9.5, offset_y=-22.5)
            ]
        )
        self._catalog["MINIFIX_15_V1"] = HardwareSpec(
            sku="MINIFIX_15_V1", manufacturer="HAFELE", model="MINIFIX_15", revision="1.0", category="CONNECTORS", price=1.5,
            host_holes=[HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, offset_x=0, offset_y=0)],
            target_holes=[
                HoleSpec(diameter=15, depth=14, face=MountFace.FRONT, offset_x=34, offset_y=0),
                HoleSpec(diameter=8, depth=34, face=MountFace.LEFT, axis="X", offset_x=0, offset_y=0)
            ]
        )
        self._catalog["CONFIRMAT_50_V1"] = HardwareSpec(
            sku="CONFIRMAT_50_V1", manufacturer="GENERIC", model="CONFIRMAT_5x50", revision="1.0", category="CONNECTORS",
            host_holes=[HoleSpec(diameter=7, depth=18, face=MountFace.LEFT, is_through_hole=True)],
            target_holes=[HoleSpec(diameter=5, depth=34, face=MountFace.LEFT, axis="X")]
        )
        self._catalog["SHELF_PIN_5MM"] = HardwareSpec(
            sku="SHELF_PIN_5MM", manufacturer="GENERIC", model="STEEL_PIN_5MM", revision="1.0", category="ACCESSORIES",
            host_holes=[HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, is_through_hole=False)],
            target_holes=[]
        )

        self._catalog["DRAWER_SLIDE_SOFTCLOSE_450"] = HardwareSpec(
            sku="DRAWER_SLIDE_SOFTCLOSE_450",
            manufacturer="GENERIC",
            model="SOFT_CLOSE_450",
            revision="1.0",
            category="DRAWER_SLIDES",
            price=20.0,
            host_holes=[
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=50.0,
                ),
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=350.0,
                ),
            ],
            target_holes=[
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=50.0,
                ),
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=350.0,
                ),
            ],
        )

        self._catalog["HANDLE_128_BLACK"] = HardwareSpec(
            sku="HANDLE_128_BLACK",
            manufacturer="GENERIC",
            model="HANDLE_128_BLACK",
            revision="1.0",
            category="HANDLES",
            price=6.0,
            host_holes=[
                HoleSpec(
                    diameter=5.0,
                    depth=18.0,
                    face=MountFace.FRONT,
                    offset_x=0.0,
                    offset_y=-64.0,
                ),
                HoleSpec(
                    diameter=5.0,
                    depth=18.0,
                    face=MountFace.FRONT,
                    offset_x=0.0,
                    offset_y=64.0,
                ),
            ],
        )

        self._catalog["CLOTHES_RAIL_1000"] = HardwareSpec(
            sku="CLOTHES_RAIL_1000",
            manufacturer="GENERIC",
            model="OVAL_RAIL_1000",
            revision="1.0",
            category="WARDROBE_ACCESSORIES"
        )

        self._catalog["ADJUSTABLE_LEG_100"] = HardwareSpec(
            sku="ADJUSTABLE_LEG_100",
            manufacturer="GENERIC",
            model="LEG_100MM",
            revision="1.0",
            category="LEGS"
        )

        self._catalog["DRAWER_SLIDE_STANDARD_450"] = HardwareSpec(
            sku="DRAWER_SLIDE_STANDARD_450",
            manufacturer="GENERIC",
            model="STANDARD_SLIDE_450",
            revision="1.0",
            category="DRAWER_SLIDES",
            price=20.0,
            host_holes=[
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=50.0,
                ),
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=350.0,
                ),
            ],
            target_holes=[
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=50.0,
                ),
                HoleSpec(
                    diameter=3.0,
                    depth=12.0,
                    face=MountFace.LEFT,
                    offset_x=32.0,
                    offset_y=350.0,
                ),
            ],
        )

        self._catalog["TOUCH_LATCH_STANDARD"] = HardwareSpec(
            sku="TOUCH_LATCH_STANDARD",
            manufacturer="GENERIC",
            model="TOUCH_LATCH",
            revision="1.0",
            category="LATCHES",
            price=45.0
        )

        self._catalog["SCREW_4X40"] = HardwareSpec(
            sku="SCREW_4X40",
            manufacturer="GENERIC",
            model="SCREW_4X40",
            revision="1.0",
            category="SCREWS",
            price=0.10
        )

        self._catalog["SCREW_3_5X16"] = HardwareSpec(
            sku="SCREW_3_5X16",
            manufacturer="GENERIC",
            model="SCREW_3.5X16",
            revision="1.0",
            category="SCREWS",
            price=0.08
        )

        self._catalog["HANDLE_STANDARD_LOW"] = HardwareSpec(
            sku="HANDLE_STANDARD_LOW",
            manufacturer="GENERIC",
            model="HANDLE_STANDARD_LOW",
            revision="1.0",
            category="HANDLES",
            price=6.0
        )

        self._catalog["HANDLE_STANDARD_MID"] = HardwareSpec(
            sku="HANDLE_STANDARD_MID",
            manufacturer="GENERIC",
            model="HANDLE_STANDARD_MID",
            revision="1.0",
            category="HANDLES",
            price=12.0
        )

        self._catalog["HANDLE_STANDARD_HIGH"] = HardwareSpec(
            sku="HANDLE_STANDARD_HIGH",
            manufacturer="GENERIC",
            model="HANDLE_STANDARD_HIGH",
            revision="1.0",
            category="HANDLES",
            price=20.0
        )

        self._catalog["SLIDING_DOOR_HANDLE_METER"] = HardwareSpec(
            sku="SLIDING_DOOR_HANDLE_METER",
            manufacturer="GENERIC",
            model="SLIDING_DOOR_HANDLE_METER",
            revision="1.0",
            category="HANDLES",
            price=30.0
        )
