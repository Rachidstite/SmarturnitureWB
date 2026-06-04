from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class FrontType(Enum):
    DOOR = "DOOR"
    DRAWER = "DRAWER"
    FAKE = "FAKE"

@dataclass
class OpeningContext:
    """يمثل الفراغ المتاح داخل الخزانة الذي سيتم تغطيته"""
    identity: str
    width: float
    height: float
    local_x: float  # X position of the opening bottom-left
    local_y: float  # Y position (vertical) of the opening bottom-left
    left_divider_thickness: float = 18.0
    right_divider_thickness: float = 18.0
    top_divider_thickness: float = 18.0
    bottom_divider_thickness: float = 18.0
    left_overlay: Optional[float] = None
    right_overlay: Optional[float] = None
    top_overlay: Optional[float] = None
    bottom_overlay: Optional[float] = None

@dataclass
class FrontElement:
    """يمثل القطعة النهائية التي ستغطي الواجهة"""
    identity: str
    front_type: FrontType
    width: float
    height: float
    local_x: float  # Cabinet-space X
    local_y: float  # Cabinet-space Y
    hinge_side: Optional[str] = None # "LEFT", "RIGHT", "TOP", "BOTTOM"

class FrontLayoutEngine:
    """
    محرك الواجهات الصناعي.
    يحسب التغطية (Overlay) والفراغات (Gaps) ويتحقق من التصادم.
    """
    
    @staticmethod
    def generate_doors_for_opening(
        opening: OpeningContext, 
        door_count: int, 
        gap: float = 2.0, 
        overlay_reduction: float = 2.0
    ) -> List[FrontElement]:
        """
        يولد أبواباً لفتحة معينة مع حساب الـ Overlay.
        overlay_reduction: المقدار المخصوم من حافة اللوح (مثلاً يغطي 16mm من أصل 18mm)
        """
        if door_count <= 0:
            return []

        # حساب التغطية (Overlay) بناءً على سماكة القواطع، أو من قيم صناعية صريحة.
        left_overlay = opening.left_overlay
        if left_overlay is None:
            left_overlay = max(0, opening.left_divider_thickness - overlay_reduction)

        right_overlay = opening.right_overlay
        if right_overlay is None:
            right_overlay = max(0, opening.right_divider_thickness - overlay_reduction)

        top_overlay = opening.top_overlay
        if top_overlay is None:
            top_overlay = max(0, opening.top_divider_thickness - overlay_reduction)

        bottom_overlay = opening.bottom_overlay
        if bottom_overlay is None:
            bottom_overlay = max(0, opening.bottom_divider_thickness - overlay_reduction)

        # العرض الإجمالي المغطى = الفتحة + التغطية يميناً ويساراً
        total_covered_width = opening.width + left_overlay + right_overlay

        if door_count == 1:
            total_covered_width -= gap
        
        # مجموع الفراغات بين الأبواب (إذا كان هناك أكثر من باب)
        internal_gaps = (door_count - 1) * gap
        
        # عرض الباب الصافي
        single_door_width = (total_covered_width - internal_gaps) / door_count
        
        # ارتفاع الباب الصافي
        door_height = opening.height

        # نقطة البداية الحقيقية (طرح التغطية اليسرى من بداية الفتحة)
        start_x = opening.local_x - left_overlay
        start_y = opening.local_y

        fronts = []
        current_x = start_x

        for i in range(door_count):
            # استراتيجية المفصلات الافتراضية (يمكن تمريرها كدالة لاحقاً)
            hinge = "LEFT" if door_count == 1 or i < (door_count / 2) else "RIGHT"

            fronts.append(FrontElement(
                identity=f"{opening.identity}_DOOR_{i+1}",
                front_type=FrontType.DOOR,
                width=single_door_width,
                height=door_height,
                local_x=current_x,
                local_y=start_y,
                hinge_side=hinge
            ))
            current_x += single_door_width + gap

        return fronts

    @staticmethod
    def validate_collisions(fronts: List[FrontElement]) -> bool:
        """
        يتحقق من تداخل الواجهات (O(n^2) بسيط لأن عدد الواجهات صغير).
        يرجع True إذا كان التوزيع سليماً.
        """
        for i, f1 in enumerate(fronts):
            for f2 in fronts[i+1:]:
                # فحص التداخل بصندوق الإحاطة (Bounding Box 2D)
                if not (f1.local_x + f1.width <= f2.local_x or 
                        f2.local_x + f2.width <= f1.local_x or 
                        f1.local_y + f1.height <= f2.local_y or 
                        f2.local_y + f2.height <= f1.local_y):
                    print(f"⚠️ Collision detected between {f1.identity} and {f2.identity}")
                    return False
        return True
