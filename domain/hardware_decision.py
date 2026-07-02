from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from domain.operational_decision import OperationalDecision


class HardwareDecisionCategory(str, Enum):
    JOINERY = "JOINERY"
    HINGE = "HINGE"
    DRAWER_SLIDE = "DRAWER_SLIDE"
    SHELF_SUPPORT = "SHELF_SUPPORT"
    BACK_PANEL_FIXING = "BACK_PANEL_FIXING"
    HANDLE = "HANDLE"
    WALL_MOUNT = "WALL_MOUNT"
    LEG = "LEG"
    FASTENER = "FASTENER"


class HardwareCompatibilityStatus(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


class HardwareInstallationComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CNC_REQUIRED = "CNC_REQUIRED"
    MANUAL_ALLOWED = "MANUAL_ALLOWED"


@dataclass(frozen=True)
class HardwareDecision:
    decision: OperationalDecision = field(default_factory=OperationalDecision)
    hardware_category: HardwareDecisionCategory = HardwareDecisionCategory.JOINERY
    selected_hardware_sku: str = ""
    candidate_hardware_skus: tuple[str, ...] = field(default_factory=tuple)
    rejected_hardware_skus: tuple[str, ...] = field(default_factory=tuple)
    compatibility_status: HardwareCompatibilityStatus = (
        HardwareCompatibilityStatus.NEEDS_REVIEW
    )
    installation_complexity: HardwareInstallationComplexity = (
        HardwareInstallationComplexity.MEDIUM
    )
    manufacturing_impact_note: str = ""
    cost_impact_note: str = ""
    quality_impact_note: str = ""
    replacement_allowed: bool = False
    replacement_reason: str = ""
