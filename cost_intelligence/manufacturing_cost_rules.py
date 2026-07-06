from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ManufacturingCostRules:
    material_area_rate: float = 120.0
    edge_meter_rate: float = 5.0
    drilling_rate: float = 1.5
    complexity_material_type_rate: float = 25.0
    panel_handling_rate: float = 0.0
    operation_rates: Dict[str, float] = field(default_factory=dict)
    overhead_flat_cost: float = 0.0
    overhead_percentage: float = 0.0
    currency: str = "MAD"

    @classmethod
    def from_pricing_catalog(cls, pricing_catalog):
        rules = cls()

        material_spec = cls._catalog_item(pricing_catalog, "MDF_18MM")
        if material_spec and "price_per_m2" in material_spec:
            rules.material_area_rate = material_spec["price_per_m2"]

        edge_spec = cls._catalog_item(pricing_catalog, "ABS_1MM")
        if edge_spec and "price_per_meter" in edge_spec:
            rules.edge_meter_rate = edge_spec["price_per_meter"]

        drilling_spec = cls._catalog_item(pricing_catalog, "MACHINING_DRILL")
        if drilling_spec and "price_per_operation" in drilling_spec:
            rules.drilling_rate = drilling_spec["price_per_operation"]

        if material_spec and "currency" in material_spec:
            rules.currency = material_spec["currency"]
        elif edge_spec and "currency" in edge_spec:
            rules.currency = edge_spec["currency"]
        elif drilling_spec and "currency" in drilling_spec:
            rules.currency = drilling_spec["currency"]

        return rules

    @staticmethod
    def _catalog_item(pricing_catalog, key):
        if pricing_catalog is None:
            return None
        if hasattr(pricing_catalog, "get"):
            return pricing_catalog.get(key) or None
        if isinstance(pricing_catalog, dict):
            return pricing_catalog.get(key)
        return getattr(pricing_catalog, key, None)
