from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_drawer_slide_capacity_rule_appears_in_report():

    drawer = SimpleNamespace(
        panel_category="drawer",
        width=1000,
        slide_type="standard",
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [drawer]
        )
    )

    assert len(report.warnings) > 0
