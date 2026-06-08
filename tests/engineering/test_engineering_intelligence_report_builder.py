from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_build_generates_warnings_and_score():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1200,
        thickness=18,
        material="MDF",
        load_class="normal",
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build([panel])
    )

    assert len(report.warnings) > 0

    assert report.score is not None

    assert report.score.score < 100
