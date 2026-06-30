from dataclasses import dataclass, field

from manufacturing.manufacturing_validation_summary_report import (
    ManufacturingValidationSummaryReport,
)


@dataclass(frozen=True)
class ProductionEvidenceView:
    cutlist_report: object = None
    machining_report: object = None
    edge_report: object = None
    hardware_report: object = None
    release_warnings: object = None
    has_cutlist_evidence: bool = False
    has_machining_evidence: bool = False
    has_edge_evidence: bool = False
    has_hardware_evidence: bool = False
    has_release_warning_evidence: bool = False


@dataclass
class ManufacturingProductionPackage:
    cutlist_report: object = None
    edge_report: object = None
    machining_report: object = None
    summary_report: object = None
    validation_summary_report: ManufacturingValidationSummaryReport | None = None
    release_ready: bool = False
    warnings: list = field(default_factory=list)
    product_bom_report: object = None
    cnc_report: object = None
    assembly_report: object = None
    hardware_report: object = None
    labels_report: object = None
    manufacturing_decision: object = None

    @property
    def manufacturing_summary(self):
        return self.summary_report

    @property
    def validation_summary(self):
        return self.validation_summary_report

    @property
    def release_warnings(self):
        return self.warnings

    @property
    def has_cutlist_evidence(self):
        return bool(getattr(self.cutlist_report, "items", None))

    @property
    def has_machining_evidence(self):
        return bool(getattr(self.machining_report, "items", None))

    @property
    def has_edge_evidence(self):
        return bool(getattr(self.edge_report, "items", None))

    @property
    def has_hardware_evidence(self):
        return bool(getattr(self.hardware_report, "bom_rows", None))

    @property
    def has_release_warning_evidence(self):
        return bool(self.release_warnings)

    @property
    def production_evidence(self):
        return ProductionEvidenceView(
            cutlist_report=self.cutlist_report,
            machining_report=self.machining_report,
            edge_report=self.edge_report,
            hardware_report=self.hardware_report,
            release_warnings=self.release_warnings,
            has_cutlist_evidence=self.has_cutlist_evidence,
            has_machining_evidence=self.has_machining_evidence,
            has_edge_evidence=self.has_edge_evidence,
            has_hardware_evidence=self.has_hardware_evidence,
            has_release_warning_evidence=self.has_release_warning_evidence,
        )
