from types import SimpleNamespace

from validation.intelligence.engineering.rules.back_panel_shear_rule import (
    BackPanelShearRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_cabinet_with_back_passes():

    cabinet = SimpleNamespace(
        cabinet_height=2200,
        cabinet_width=800,
        has_back_panel=True,
    )

    result = (
        BackPanelShearRule()
        .validate(cabinet)
    )

    assert result.passed is True


def test_large_cabinet_warns():

    cabinet = SimpleNamespace(
        cabinet_height=2400,
        cabinet_width=1200,
        has_back_panel=False,
    )

    result = (
        BackPanelShearRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_cabinet_fails():

    cabinet = SimpleNamespace(
        cabinet_height=2800,
        cabinet_width=1600,
        has_back_panel=False,
    )

    result = (
        BackPanelShearRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
