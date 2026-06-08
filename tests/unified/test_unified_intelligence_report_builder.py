from types import SimpleNamespace

from validation.intelligence.unified.unified_intelligence_report_builder import (
    UnifiedIntelligenceReportBuilder,
)


def test_build_generates_unified_report():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1200,
        thickness=18,
        material="MDF",
        load_class="normal",
    )

    report = (
        UnifiedIntelligenceReportBuilder()
        .build([panel])
    )

    assert report is not None

    assert len(report.warnings) > 0

    assert report.score is not None

    assert report.score.score < 100
