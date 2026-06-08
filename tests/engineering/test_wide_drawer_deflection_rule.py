from types import SimpleNamespace

from validation.intelligence.engineering.rules.wide_drawer_deflection_rule import (
    WideDrawerDeflectionRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_drawer_passes():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=700,
        thickness=6,
    )

    result = (
        WideDrawerDeflectionRule()
        .validate(panel)
    )

    assert result.passed is True


def test_wide_drawer_warns():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=1000,
        thickness=6,
    )

    result = (
        WideDrawerDeflectionRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_drawer_fails():

    panel = SimpleNamespace(
        panel_category="drawer_bottom",
        width=1200,
        thickness=6,
    )

    result = (
        WideDrawerDeflectionRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
