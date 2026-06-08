from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_hanging_cabinet_rule_appears_in_report():

    cabinet = SimpleNamespace(
        cabinet_type="wall_cabinet",
        width=1200,
        mounting_points=2,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [cabinet]
        )
    )

    assert len(report.warnings) > 0
