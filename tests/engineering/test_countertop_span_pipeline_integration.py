from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_countertop_span_rule_appears_in_report():

    panel = SimpleNamespace(
        panel_category="countertop",
        span=1400,
        thickness=36,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [panel]
        )
    )

    assert len(report.warnings) > 0
