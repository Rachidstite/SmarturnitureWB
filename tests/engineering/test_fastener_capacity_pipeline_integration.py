from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_fastener_capacity_rule_appears_in_report():

    joint = SimpleNamespace(
        load=80,
        fastener_count=2,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [joint]
        )
    )

    assert len(report.warnings) > 0
