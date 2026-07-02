from cost_intelligence.manufacturing_optimization_result import (
    ManufacturingOptimizationResult,
)
from cost_intelligence.nesting_intelligence_builder import (
    NestingIntelligenceBuilder,
)
from cost_intelligence.offcut_classifier import OffcutClassifier
from cost_intelligence.offcut_extraction_service import OffcutExtractionService
from cost_intelligence.offcut_intelligence_builder import (
    OffcutIntelligenceBuilder,
)
from cost_intelligence.offcut_reuse_policy import OffcutReusePolicy
from cost_intelligence.offcut_report_builder import OffcutReportBuilder
from cost_intelligence.sheet_utilization_builder import SheetUtilizationBuilder
from cost_intelligence.waste_intelligence_builder import WasteIntelligenceBuilder


class ManufacturingOptimizationPipelineBuilder:

    def build(self, sheet_results, consumption_report, cost_estimate):
        sheet_utilization_report = SheetUtilizationBuilder().build(sheet_results)
        offcuts = OffcutExtractionService.extract(sheet_results)
        if hasattr(offcuts, "__iter__"):
            policy = OffcutReusePolicy(
                material="",
                thickness=0,
                min_width=80,
                min_height=80,
                min_area=10000,
            )
            classifier = OffcutClassifier(policy=policy)
            for offcut in offcuts:
                classification = classifier.classify(offcut)
                offcut.reusable = bool(classification.reusable)
        offcut_report = OffcutReportBuilder().build(offcuts)
        offcut_intelligence_report = OffcutIntelligenceBuilder().build(
            offcut_report
        )
        waste_intelligence_report = WasteIntelligenceBuilder().build(
            consumption_report,
            cost_estimate,
            offcut_intelligence_report,
        )
        nesting_intelligence_report = NestingIntelligenceBuilder().build(
            sheet_utilization_report,
            offcut_intelligence_report,
            waste_intelligence_report,
        )
        return ManufacturingOptimizationResult(
            sheet_utilization_report=sheet_utilization_report,
            offcut_report=offcut_report,
            offcut_intelligence_report=offcut_intelligence_report,
            waste_intelligence_report=waste_intelligence_report,
            nesting_intelligence_report=nesting_intelligence_report,
        )
