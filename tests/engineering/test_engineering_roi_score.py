from validation.intelligence.engineering.roi.engineering_roi_engine import (
    EngineeringROIEngine,
)


def test_excellent_roi_has_high_score():

    roi = (
        EngineeringROIEngine()
        .evaluate(
            "SHELF_DEFLECTION"
        )
    )

    assert roi.score >= 90


def test_unknown_roi_has_low_score():

    roi = (
        EngineeringROIEngine()
        .evaluate(
            "UNKNOWN"
        )
    )

    assert roi.score <= 30
