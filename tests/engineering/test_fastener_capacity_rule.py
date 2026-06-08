from types import SimpleNamespace

from validation.intelligence.engineering.rules.fastener_capacity_rule import (
    FastenerCapacityRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_joint_passes():

    joint = SimpleNamespace(
        load=30,
        fastener_count=4,
    )

    result = (
        FastenerCapacityRule()
        .validate(joint)
    )

    assert result.passed is True
    assert result.level == EngineeringLevel.INFO


def test_under_fastened_joint_warns():

    joint = SimpleNamespace(
        load=80,
        fastener_count=2,
    )

    result = (
        FastenerCapacityRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_critical_joint_fails():

    joint = SimpleNamespace(
        load=150,
        fastener_count=2,
    )

    result = (
        FastenerCapacityRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
