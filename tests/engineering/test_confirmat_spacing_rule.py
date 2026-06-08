from types import SimpleNamespace

from validation.intelligence.engineering.rules.confirmat_spacing_rule import (
    ConfirmatSpacingRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_short_joint_passes():

    joint = SimpleNamespace(
        joint_length=300,
    )

    result = (
        ConfirmatSpacingRule()
        .validate(joint)
    )

    assert result.passed is True
    assert result.level == EngineeringLevel.INFO


def test_medium_joint_warns():

    joint = SimpleNamespace(
        joint_length=800,
    )

    result = (
        ConfirmatSpacingRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_long_joint_fails():

    joint = SimpleNamespace(
        joint_length=1500,
    )

    result = (
        ConfirmatSpacingRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
