from dataclasses import dataclass, field

from manufacturing.drawer_decision_report import DrawerDecisionReport
from manufacturing.drawer_validation_report import DrawerValidationReport
from manufacturing.drawer_structural_report import DrawerStructuralReport


@dataclass
class DrawerIntelligenceReport:
    validation: DrawerValidationReport = field(default_factory=DrawerValidationReport)
    structural: DrawerStructuralReport = field(default_factory=DrawerStructuralReport)
    decision: DrawerDecisionReport = field(default_factory=DrawerDecisionReport)
