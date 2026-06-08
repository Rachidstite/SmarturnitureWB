from types import SimpleNamespace

from validation.intelligence.engineering.rules.anchoring_required_rule import (
    AnchoringRequiredRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_cabinet_passes():

    cabinet = SimpleNamespace(
        cabinet_height=2200,
        cabinet_depth=600,
    )

    result = (
        AnchoringRequiredRule()
        .validate(cabinet)
    )

    assert result.passed is True
    assert result.level == EngineeringLevel.INFO


def test_tall_cabinet_warns():

    cabinet = SimpleNamespace(
        cabinet_height=2600,
        cabinet_depth=450,
    )

    result = (
        AnchoringRequiredRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_cabinet_fails():

    cabinet = SimpleNamespace(
        cabinet_height=3200,
        cabinet_depth=350,
    )

    result = (
        AnchoringRequiredRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
