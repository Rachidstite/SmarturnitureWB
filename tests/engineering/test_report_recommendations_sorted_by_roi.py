from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)


def test_report_recommendations_sorted_by_priority_and_roi():

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

    priorities = [
        (
            r.priority,
            r.roi_score,
        )
        for r in report.recommendations
    ]

    assert priorities == sorted(
        priorities,
        key=lambda x: (
            {
                "CRITICAL": 0,
                "HIGH": 1,
                "MEDIUM": 2,
                "LOW": 3,
            }.get(x[0], 999),
            -x[1],
        ),
    )
