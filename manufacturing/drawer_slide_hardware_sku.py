from dataclasses import dataclass


@dataclass
class DrawerSlideHardwareSku:
    sku: str = ""
    manufacturer: str = ""
    model: str = ""
    revision: str = ""
    category: str = ""
    price: float = 0.0
