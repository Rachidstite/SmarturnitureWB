from types import SimpleNamespace

from validation.intelligence.engineering.rules.connector_recommendation_rule import (
    ConnectorRecommendationRule,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


def test_small_joint_passes():

    joint = SimpleNamespace(
        joint_length=250,
    )

    result = (
        ConnectorRecommendationRule()
        .validate(joint)
    )

    assert result.passed is True
    assert result.level == EngineeringLevel.INFO


def test_medium_joint_recommends_connector():

    joint = SimpleNamespace(
        joint_length=800,
    )

    result = (
        ConnectorRecommendationRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.WARNING


def test_large_joint_requires_heavy_connector():

    joint = SimpleNamespace(
        joint_length=1500,
    )

    result = (
        ConnectorRecommendationRule()
        .validate(joint)
    )

    assert result.passed is False
    assert result.level == EngineeringLevel.ERROR
