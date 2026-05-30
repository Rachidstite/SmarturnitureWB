from dataclasses import dataclass
from typing import List, Optional
from exports.heuristics import PlacementHeuristics

@dataclass
class FreeRect:
    x: float
    y: float
    w: float
    h: float
    
    @property
    def area(self) -> float:
        return self.w * self.h

@dataclass
class UsedRect:
    x: float
    y: float
    w: float
    h: float

class SpaceManager:
    def __init__(self, sheet_width: float, sheet_height: float):
        self.free_rects: List[FreeRect] = [FreeRect(0, 0, sheet_width, sheet_height)]

    def place_rect(self, used: UsedRect):
        new_free_rects = []
        for free in self.free_rects:
            if self._intersect(free, used):
                splits = self._split(free, used)
                # Rect Normalization: تصفية المساحات السالبة أو الصفرية فوراً
                valid_splits = [r for r in splits if r.w > 0.1 and r.h > 0.1]
                new_free_rects.extend(valid_splits)
            else:
                new_free_rects.append(free)
                
        self.free_rects = new_free_rects
        self._prune_redundant_rects()

    def find_position(self, w: float, h: float, heuristic: str = "BSSF") -> Optional[FreeRect]:
        """واجهة استخدام الـ Heuristics للبحث عن أفضل مكان"""
        if heuristic == "BAF":
            best_node, score = PlacementHeuristics.best_area_fit(self.free_rects, w, h)
        elif heuristic == "BLF":
            best_node, score = PlacementHeuristics.bottom_left_fit(self.free_rects, w, h)
        else: # Default BSSF
            best_node, score = PlacementHeuristics.best_short_side_fit(self.free_rects, w, h)
            
        return best_node

    def _intersect(self, free: FreeRect, used: UsedRect) -> bool:
        return not (used.x >= free.x + free.w or used.x + used.w <= free.x or
                    used.y >= free.y + free.h or used.y + used.h <= free.y)

    def _split(self, free: FreeRect, used: UsedRect) -> List[FreeRect]:
        splits = []
        if used.y > free.y:
            splits.append(FreeRect(free.x, free.y, free.w, used.y - free.y))
        if used.y + used.h < free.y + free.h:
            splits.append(FreeRect(free.x, used.y + used.h, free.w, (free.y + free.h) - (used.y + used.h)))
        if used.x > free.x:
            splits.append(FreeRect(free.x, free.y, used.x - free.x, free.h))
        if used.x + used.w < free.x + free.w:
            splits.append(FreeRect(used.x + used.w, free.y, (free.x + free.w) - (used.x + used.w), free.h))
        return splits

    def _prune_redundant_rects(self):
        pruned = []
        for i, r1 in enumerate(self.free_rects):
            is_contained = False
            for j, r2 in enumerate(self.free_rects):
                if i != j:
                    if (r1.x >= r2.x and r1.y >= r2.y and 
                        r1.x + r1.w <= r2.x + r2.w and r1.y + r1.h <= r2.y + r2.h):
                        is_contained = True
                        break
            if not is_contained:
                pruned.append(r1)
        self.free_rects = pruned
