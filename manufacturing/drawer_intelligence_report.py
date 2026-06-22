from dataclasses import dataclass, field

from manufacturing.drawer_decision_report import DrawerDecisionReport
from manufacturing.drawer_validation_report import DrawerValidationReport


@dataclass
class DrawerIntelligenceReport:
    validation: DrawerValidationReport = field(default_factory=DrawerValidationReport)
    decision: DrawerDecisionReport = field(default_factory=DrawerDecisionReport)
