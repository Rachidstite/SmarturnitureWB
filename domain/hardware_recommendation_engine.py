from dataclasses import dataclass
from typing import Optional

"""
Hardware Recommendation Engine V1

Additive recommendation layer.

Does not modify:
- SceneGraph
- ManufacturingCompiler
- Validators
- HardwareRegistry
"""


CONFIRMAT_MAX_SPAN = 600.0
MINIFIX_MAX_SPAN = 1000.0


@dataclass(frozen=True)
class HardwareRecommendation:
    hardware_id: str
    hardware_type: str
    reason: str
    confidence: str


class HardwareRecommendationEngine:
    """
    V1 recommendation engine.

    Initial scope:
    - SHELF recommendations only

    Future versions may support:
    - DIVIDER
    - TOP_PANEL
    - BOTTOM_PANEL
    - Drawer systems
    - Door systems
    """

    def recommend(
        self,
        role: str,
        span: float,
        thickness: float,
    ) -> Optional[HardwareRecommendation]:

        if role != "SHELF":
            return None

        if span <= CONFIRMAT_MAX_SPAN:
            return HardwareRecommendation(
                hardware_id="CONFIRMAT_50_V1",
                hardware_type="CONFIRMAT",
                reason="Small shelf span",
                confidence="HIGH",
            )

        if span <= MINIFIX_MAX_SPAN:
            return HardwareRecommendation(
                hardware_id="MINIFIX_15_V1",
                hardware_type="MINIFIX",
                reason="Medium shelf span",
                confidence="HIGH",
            )

        return HardwareRecommendation(
            hardware_id="MINIFIX_15_V1",
            hardware_type="MINIFIX",
            reason="Large span. Recommend dowel-assisted assembly",
            confidence="MEDIUM",
        )
