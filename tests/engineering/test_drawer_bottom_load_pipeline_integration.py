from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_drawer_bottom_load_rule_appears_in_report():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=1000,
        thickness=6,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [panel]
        )
    )

    assert len(report.warnings) > 0
