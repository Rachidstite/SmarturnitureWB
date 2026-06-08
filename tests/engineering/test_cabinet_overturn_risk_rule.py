from types import SimpleNamespace

from validation.intelligence.engineering.rules.cabinet_overturn_risk_rule import (
    CabinetOverturnRiskRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_stable_cabinet_passes():

    cabinet = SimpleNamespace(
        cabinet_height=2200,
        cabinet_depth=600,
    )

    result = (
        CabinetOverturnRiskRule()
        .validate(cabinet)
    )

    assert result.passed is True


def test_tall_shallow_cabinet_warns():

    cabinet = SimpleNamespace(
        cabinet_height=2800,
        cabinet_depth=450,
    )

    result = (
        CabinetOverturnRiskRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_overturn_risk_fails():

    cabinet = SimpleNamespace(
        cabinet_height=3200,
        cabinet_depth=350,
    )

    result = (
        CabinetOverturnRiskRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
