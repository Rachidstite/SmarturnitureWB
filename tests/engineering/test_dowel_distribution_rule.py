from types import SimpleNamespace

from validation.intelligence.engineering.rules.dowel_distribution_rule import (
    DowelDistributionRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_normal_joint_passes():

    joint = SimpleNamespace(
        joint_length=300,
        dowel_count=2,
    )

    result = (
        DowelDistributionRule()
        .validate(joint)
    )

    assert result.passed is True
    assert result.level == EngineeringLevel.INFO


def test_under_doweled_joint_warns():

    joint = SimpleNamespace(
        joint_length=800,
        dowel_count=2,
    )

    result = (
        DowelDistributionRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_severely_under_doweled_joint_fails():

    joint = SimpleNamespace(
        joint_length=1500,
        dowel_count=2,
    )

    result = (
        DowelDistributionRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
