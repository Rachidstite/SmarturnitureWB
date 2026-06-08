from validation.intelligence.unified.unified_report_builder import (
    UnifiedReportBuilder,
)

from validation.intelligence.engineering.engineering_report import (
    EngineeringReport,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


def test_builder_merges_reports():

    manufacturing = ManufacturingIntelligenceReport(
        errors=[],
        warnings=[object()],
    )

    engineering = EngineeringReport(
        errors=[object()],
        warnings=[],
    )

    report = (
        UnifiedReportBuilder()
        .build(
            manufacturing,
            engineering,
        )
    )

    assert len(report.errors) == 1
    assert len(report.warnings) == 1
