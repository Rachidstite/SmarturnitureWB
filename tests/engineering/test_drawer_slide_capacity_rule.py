from types import SimpleNamespace

from validation.intelligence.engineering.rules.drawer_slide_capacity_rule import (
    DrawerSlideCapacityRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_drawer_passes():

    drawer = SimpleNamespace(
        panel_category="drawer",
        width=700,
        slide_type="standard",
    )

    result = (
        DrawerSlideCapacityRule()
        .validate(drawer)
    )

    assert result.passed is True


def test_wide_drawer_warns():

    drawer = SimpleNamespace(
        panel_category="drawer",
        width=1000,
        slide_type="standard",
    )

    result = (
        DrawerSlideCapacityRule()
        .validate(drawer)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_drawer_fails():

    drawer = SimpleNamespace(
        panel_category="drawer",
        width=1300,
        slide_type="standard",
    )

    result = (
        DrawerSlideCapacityRule()
        .validate(drawer)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
