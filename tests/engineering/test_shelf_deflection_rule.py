from types import SimpleNamespace

from validation.intelligence.engineering.rules.shelf_deflection_rule import (
    ShelfDeflectionRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_short_shelf_passes():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=800,
        thickness=18,
        material="MDF",
        load_class="normal",
    )

    result = (
        ShelfDeflectionRule()
        .validate(panel)
    )

    assert result.passed is True


def test_medium_shelf_warns():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1000,
        thickness=18,
        material="MDF",
        load_class="normal",
    )

    result = (
        ShelfDeflectionRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_long_shelf_fails():

    panel = SimpleNamespace(
        panel_category="shelf",
        span=1300,
        thickness=18,
        material="MDF",
        load_class="normal",
    )

    result = (
        ShelfDeflectionRule()
        .validate(panel)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
