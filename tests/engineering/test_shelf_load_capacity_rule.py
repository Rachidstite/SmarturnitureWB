from types import SimpleNamespace

from validation.intelligence.engineering.rules.shelf_load_capacity_rule import (
    ShelfLoadCapacityRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_shelf_passes():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=800,
        thickness=18,
    )

    result = (
        ShelfLoadCapacityRule()
        .validate(panel)
    )

    assert result.passed is True


def test_heavy_span_warns():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1200,
        thickness=18,
    )

    result = (
        ShelfLoadCapacityRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_span_fails():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1600,
        thickness=18,
    )

    result = (
        ShelfLoadCapacityRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
