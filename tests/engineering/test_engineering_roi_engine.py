from validation.intelligence.engineering.roi.engineering_roi_engine import (
    EngineeringROIEngine,
)


def test_shelf_deflection_has_excellent_roi():

    roi = (
        EngineeringROIEngine()
        .evaluate(
            "SHELF_DEFLECTION"
        )
    )

    assert roi.rating == "EXCELLENT"


def test_unknown_code_returns_low_roi():

    roi = (
        EngineeringROIEngine()
        .evaluate(
            "UNKNOWN"
        )
    )

    assert roi.rating == "LOW"
