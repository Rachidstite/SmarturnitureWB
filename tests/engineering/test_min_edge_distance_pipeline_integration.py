from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_min_edge_distance_rule_appears_in_report():

    joint = SimpleNamespace(
        edge_distance=25,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [joint]
        )
    )

    assert len(report.warnings) > 0
