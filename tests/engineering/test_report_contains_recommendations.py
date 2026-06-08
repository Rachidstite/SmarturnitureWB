from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_report_contains_recommendations():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1200,
        thickness=18,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [panel]
        )
    )

    assert len(
        report.recommendations
    ) > 0
