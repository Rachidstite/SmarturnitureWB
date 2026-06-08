from types import SimpleNamespace

from validation.intelligence.engineering.rules.upper_cabinet_span_rule import (
    UpperCabinetSpanRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_upper_cabinet_passes():

    cabinet = SimpleNamespace(
        cabinet_type="upper_cabinet",
        width=800,
    )

    result = (
        UpperCabinetSpanRule()
        .validate(cabinet)
    )

    assert result.passed is True


def test_wide_upper_cabinet_warns():

    cabinet = SimpleNamespace(
        cabinet_type="upper_cabinet",
        width=1200,
    )

    result = (
        UpperCabinetSpanRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_extreme_upper_cabinet_fails():

    cabinet = SimpleNamespace(
        cabinet_type="upper_cabinet",
        width=1600,
    )

    result = (
        UpperCabinetSpanRule()
        .validate(cabinet)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
