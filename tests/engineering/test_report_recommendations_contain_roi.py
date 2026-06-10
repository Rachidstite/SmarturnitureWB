from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_report_recommendations_contain_roi():

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

    recommendation = report.recommendations[0]

    assert hasattr(
        recommendation,
        "roi_rating",
    )

    assert hasattr(
        recommendation,
        "roi_score",
    )
