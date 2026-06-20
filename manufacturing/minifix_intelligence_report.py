from dataclasses import dataclass, field

from manufacturing.minifix_decision_report import MinifixDecisionReport
from manufacturing.minifix_hardware_sku import MinifixHardwareSku
from manufacturing.minifix_pattern_report import MinifixPatternReport
from manufacturing.minifix_placement_report import MinifixPlacementReport
from manufacturing.minifix_rule_report import MinifixRuleReport
from manufacturing.minifix_validation_report import MinifixValidationReport


@dataclass
class MinifixIntelligenceReport:
    hardware_sku: MinifixHardwareSku = field(default_factory=MinifixHardwareSku)
    placement: MinifixPlacementReport = field(default_factory=MinifixPlacementReport)
    pattern: MinifixPatternReport = field(default_factory=MinifixPatternReport)
    rules: MinifixRuleReport = field(default_factory=MinifixRuleReport)
    validation: MinifixValidationReport = field(default_factory=MinifixValidationReport)
    decision: MinifixDecisionReport = field(default_factory=MinifixDecisionReport)
