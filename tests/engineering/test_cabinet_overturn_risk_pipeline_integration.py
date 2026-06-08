from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_cabinet_overturn_rule_appears_in_report():

    cabinet = SimpleNamespace(
        cabinet_height=2800,
        cabinet_depth=450,
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            [cabinet]
        )
    )

    assert len(report.warnings) > 0
