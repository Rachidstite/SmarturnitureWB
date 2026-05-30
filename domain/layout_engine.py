from dataclasses import dataclass
from typing import List

@dataclass
class DoorSpec:
    width: float
    x_position: float
    hinge_side: str  # "LEFT" or "RIGHT"

class DoorClusterEngine:
    """
    محرك التوزيع الشامل للأبواب.
    يعالج الواجهة ككتلة واحدة لمنع تداخل الأبواب الوسطية.
    """
    @staticmethod
    def compute_layout(total_opening_width: float, door_count: int, gap: float = 2.0) -> List[DoorSpec]:
        """
        يحسب عرض وموقع كل باب مع ضمان وجود فراغات (Gaps) صحيحة.
        المعادلة: العرض الصافي = العرض الكلي - (عدد الفراغات * حجم الفراغ)
        """
        if door_count <= 0:
            return []

        # عدد الفراغات دائماً أكبر من عدد الأبواب بواحد (يمين، يسار، وبين الأبواب)
        total_gaps_width = (door_count + 1) * gap
        
        # العرض الصافي للباب الواحد
        single_door_width = (total_opening_width - total_gaps_width) / door_count
        
        doors = []
        current_x = gap # نبدأ من أول فراغ على اليسار
        
        for i in range(door_count):
            # تحديد جهة المفصلة (منطقي صناعياً: الأبواب تفتح من المنتصف للخارج)
            hinge = "LEFT" if i < (door_count / 2) else "RIGHT"
            
            doors.append(DoorSpec(
                width=single_door_width,
                x_position=current_x,
                hinge_side=hinge
            ))
            
            # تحريك المؤشر للباب التالي (عرض الباب + الفراغ)
            current_x += single_door_width + gap
            
        return doors
