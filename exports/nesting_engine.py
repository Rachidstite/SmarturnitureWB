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
        
        for item in cutlist_items:
            mat = item.material
            if mat not in materials_baskets:
                materials_baskets[mat] = []
                
            role = str(getattr(item, 'role', 'PART')).split('.')[-1]
            semantic_name = f"{role}_{int(item.cut_width)}x{int(item.cut_height)}"
            can_rotate = (item.grain_direction in ["NONE", None, ""])
            
            materials_baskets[mat].append(NestingPart(
                semantic_name=semantic_name,
                width=item.cut_width,
                height=item.cut_height,
                can_rotate=can_rotate
            ))
            
        results = {}
        for mat, parts in materials_baskets.items():
            # حقن الاستراتيجية لتقوم بعملية التعشيق
            results[mat] = self.strategy.pack(parts, self.sheet_width, self.sheet_height, self.kerf)
            
        return results
