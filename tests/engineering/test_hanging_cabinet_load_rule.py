from types import SimpleNamespace

from validation.intelligence.engineering.rules.hanging_cabinet_load_rule import (
    HangingCabinetLoadRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_wall_cabinet_passes():

    cabinet = SimpleNamespace(
        cabinet_type="wall_cabinet",
        width=800,
        mounting_points=2,
    )

    result = (
        HangingCabinetLoadRule()
        .validate(cabinet)
    )

    assert result.passed is True


def test_wide_wall_cabinet_warns():

    cabinet = SimpleNamespace(
        cabinet_type="wall_cabinet",
        width=1200,
        mounting_points=2,
    )

    result = (
        HangingCabinetLoadRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_very_wide_wall_cabinet_fails():

    cabinet = SimpleNamespace(
        cabinet_type="wall_cabinet",
        width=1600,
        mounting_points=2,
    )

    result = (
        HangingCabinetLoadRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
