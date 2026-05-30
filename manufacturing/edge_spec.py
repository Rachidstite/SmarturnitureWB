from dataclasses import dataclass, field
from typing import Optional, Dict
from shared.roles import NodeRole

@dataclass
class EdgeSpec:
    """مواصفات شريط اللصق لكل حافة."""
    top: Optional[str] = None      # "ABS_1MM", "PVC_2MM", None
    bottom: Optional[str] = None
    left: Optional[str] = None
    right: Optional[str] = None

    def all_banded(self) -> Dict[str, str]:
        """يرجع قائمة الحواف التي تحتاج شريط لصق."""
        result = {}
        if self.top: result["TOP"] = self.top
        if self.bottom: result["BOTTOM"] = self.bottom
        if self.left: result["LEFT"] = self.left
        if self.right: result["RIGHT"] = self.right
        return result

    def linear_meters(self, width: float, height: float) -> float:
        """يحسب الأمتار الطولية لشريط اللصق."""
        total = 0.0
        if self.top: total += width / 1000.0
        if self.bottom: total += width / 1000.0
        if self.left: total += height / 1000.0
        if self.right: total += height / 1000.0
        return round(total, 3)

class EdgeBandRegistry:
    """يعرف تلقائياً الحواف التي تحتاج شريط لصق حسب الدور التصنيعي."""

    # القواعد: لكل دور، أي الحواف تحتاج شريط لصق (افتراضياً ABS_1MM)
    RULES = {
        NodeRole.SIDE_PANEL:    EdgeSpec(top=None, bottom=None, left=None, right="ABS_1MM"),  # الحافة الأمامية فقط
        NodeRole.TOP_PANEL:     EdgeSpec(top=None, bottom=None, left=None, right="ABS_1MM"),  # الحافة الأمامية
        NodeRole.BOTTOM_PANEL:  EdgeSpec(top=None, bottom=None, left=None, right="ABS_1MM"),
        NodeRole.SHELF:         EdgeSpec(top=None, bottom=None, left=None, right="ABS_1MM"),  # Front edge
        NodeRole.DIVIDER:       EdgeSpec(top=None, bottom=None, left=None, right="ABS_1MM"),
        NodeRole.DOOR_PANEL:    EdgeSpec(top="ABS_1MM", bottom="ABS_1MM", left="ABS_1MM", right="ABS_1MM"),  # 4 جوانب
        NodeRole.DRAWER_FACE:   EdgeSpec(top="ABS_1MM", bottom="ABS_1MM", left="ABS_1MM", right="ABS_1MM"),
        NodeRole.PLINTH:        EdgeSpec(top=None, bottom=None, left=None, right="ABS_1MM"),
        NodeRole.BACK_PANEL:    EdgeSpec(top=None, bottom=None, left=None, right=None),  # الظهر لا يحتاج شريط
    }

    @classmethod
    def get_edges(cls, role: NodeRole) -> EdgeSpec:
        """يرجع حواف الدور المطلوب، أو حواف فارغة إذا لم يُعرف."""
        return cls.RULES.get(role, EdgeSpec())
