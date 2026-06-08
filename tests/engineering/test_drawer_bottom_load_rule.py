from types import SimpleNamespace

from validation.intelligence.engineering.rules.drawer_bottom_load_rule import (
    DrawerBottomLoadRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_drawer_bottom_passes():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=700,
        thickness=6,
    )

    result = (
        DrawerBottomLoadRule()
        .validate(panel)
    )

    assert result.passed is True


def test_wide_drawer_bottom_warns():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=1000,
        thickness=6,
    )

    result = (
        DrawerBottomLoadRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_drawer_bottom_fails():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=1300,
        thickness=6,
    )

    result = (
        DrawerBottomLoadRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
