from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_dowel_distribution_rule_appears_in_report():

    joint = SimpleNamespace(
        joint_length=800,
        dowel_count=2,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [joint]
        )
    )

    assert len(report.warnings) > 0
