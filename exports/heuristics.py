import math
from typing import Optional, Tuple
from exports.space_manager import FreeRect

class PlacementHeuristics:
    """
    محرك الاستدلال لاختيار أفضل فراغ متاح.
    يرجع (أفضل فراغ، النتيجة/Score). كلما كانت النتيجة أقل، كان الاختيار أفضل.
    """
    
    @staticmethod
    def best_area_fit(free_rects: list, w: float, h: float) -> Tuple[Optional[FreeRect], float]:
        """BAF: يبحث عن الفراغ الذي مساحته أقرب ما يمكن لمساحة القطعة (تقليل الهدر المباشر)"""
        best_node = None
        best_area_fit = float('inf')
        best_short_side_fit = float('inf')
        
        part_area = w * h
        
        for free in free_rects:
            if free.w >= w and free.h >= h:
                area_fit = free.area - part_area
                short_side_fit = min(free.w - w, free.h - h)
                
                # نستخدم short_side كعامل كسر تعادل (Tie-breaker)
                if area_fit < best_area_fit or (area_fit == best_area_fit and short_side_fit < best_short_side_fit):
                    best_node = free
                    best_area_fit = area_fit
                    best_short_side_fit = short_side_fit
                    
        return best_node, best_area_fit

    @staticmethod
    def best_short_side_fit(free_rects: list, w: float, h: float) -> Tuple[Optional[FreeRect], float]:
        """BSSF: يقلل المساحة المتبقية على الضلع الأقصر، يترك مساحات طولية ممتازة للاستخدام اللاحق"""
        best_node = None
        best_short_side_fit = float('inf')
        best_area_fit = float('inf')
        
        for free in free_rects:
            if free.w >= w and free.h >= h:
                short_side_fit = min(free.w - w, free.h - h)
                area_fit = free.area - (w * h)
                
                if short_side_fit < best_short_side_fit or (short_side_fit == best_short_side_fit and area_fit < best_area_fit):
                    best_node = free
                    best_short_side_fit = short_side_fit
                    best_area_fit = area_fit
                    
        return best_node, best_short_side_fit

    @staticmethod
    def bottom_left_fit(free_rects: list, w: float, h: float) -> Tuple[Optional[FreeRect], float]:
        """BLF: يدفع القطع لأسفل اللوح ثم لليسار. ممتاز للاستقرار."""
        best_node = None
        best_y = float('inf')
        best_x = float('inf')
        
        for free in free_rects:
            if free.w >= w and free.h >= h:
                if free.y < best_y or (free.y == best_y and free.x < best_x):
                    best_node = free
                    best_y = free.y
                    best_x = free.x
                    
        # في BLF النتيجة هي إحداثي Y لتتوافق مع معيار "الأقل هو الأفضل"
        return best_node, best_y
