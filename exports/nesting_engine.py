import inspect
from typing import Dict, List
from exports.strategies import PlacementStrategy, GuillotineStripStrategy, SheetResult
from dataclasses import dataclass

@dataclass
class NestingPart:
    semantic_name: str
    width: float
    height: float
    can_rotate: bool

class IndustrialNestingEngine:
    """
    محرك التعشيق الصناعي القائم على الاستراتيجيات (Strategy-based Engine).
    """
    def __init__(self, strategy: PlacementStrategy, sheet_width: float = 2440.0, sheet_height: float = 1220.0, saw_kerf: float = 4.0):
        self.strategy = strategy
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.kerf = saw_kerf

    def process(self, cutlist_items) -> Dict[str, List[SheetResult]]:
        materials_baskets = {}
        materials_context = {}
        
        for item in cutlist_items:
            thickness = item.thickness
            thickness_label = f"{thickness:g}MM"
            material = str(item.material)

            if material.upper().endswith(
                f"_{thickness_label}".upper()
            ):
                stock_key = material
            else:
                stock_key = (
                    f"{material}_{thickness_label}"
                )
            if stock_key not in materials_baskets:
                materials_baskets[stock_key] = []
                materials_context[stock_key] = (
                    material,
                    thickness,
                )
                
            role = str(getattr(item, 'role', 'PART')).split('.')[-1]
            part_width = getattr(item, "cut_width", None)
            if part_width is None:
                part_width = item.width
            part_height = getattr(item, "cut_height", None)
            if part_height is None:
                part_height = item.height
            grain_direction = getattr(item, "grain_direction", "NONE")
            semantic_name = f"{role}_{int(part_width)}x{int(part_height)}"
            can_rotate = (grain_direction in ["NONE", None, ""])
            
            for _ in range(getattr(item, "quantity", 1)):
                materials_baskets[stock_key].append(NestingPart(
                    semantic_name=semantic_name,
                    width=part_width,
                    height=part_height,
                    can_rotate=can_rotate
                ))
            
        results = {}
        for mat, parts in materials_baskets.items():
            # حقن الاستراتيجية لتقوم بعملية التعشيق
            material, thickness = materials_context[mat]
            pack_signature = inspect.signature(self.strategy.pack)
            accepts_stock_metadata = any(
                param.kind == inspect.Parameter.VAR_KEYWORD
                for param in pack_signature.parameters.values()
            ) or (
                "material" in pack_signature.parameters
                and "thickness" in pack_signature.parameters
            )

            if accepts_stock_metadata:
                results[mat] = self.strategy.pack(
                    parts,
                    self.sheet_width,
                    self.sheet_height,
                    self.kerf,
                    material=material,
                    thickness=thickness,
                )
            else:
                results[mat] = self.strategy.pack(
                    parts,
                    self.sheet_width,
                    self.sheet_height,
                    self.kerf,
                )
            
        return results
