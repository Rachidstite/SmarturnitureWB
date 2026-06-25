from project_engineering.motion_envelope_fact import MotionEnvelopeFact
from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_motion_envelope_overlap(
    moving_envelope: MotionEnvelopeFact,
    obstacle_envelope: MotionEnvelopeFact,
    rule_id: str = "MOTION_ENVELOPE_OVERLAP",
    source: str = "",
) -> OperationalRuleResult:
    overlaps = (
        moving_envelope.x_min < obstacle_envelope.x_max
        and moving_envelope.x_max > obstacle_envelope.x_min
        and moving_envelope.y_min < obstacle_envelope.y_max
        and moving_envelope.y_max > obstacle_envelope.y_min
        and moving_envelope.z_min < obstacle_envelope.z_max
        and moving_envelope.z_max > obstacle_envelope.z_min
    )

    if not overlaps:
        return OperationalRuleResult(
            rule_id=rule_id,
            capability="motion",
            component_id=moving_envelope.component_id,
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="motion",
        component_id=moving_envelope.component_id,
        passed=False,
        severity="error",
        message=(
            "Motion envelopes overlap between "
            f"{moving_envelope.component_id} and {obstacle_envelope.component_id}"
        ),
        source=source,
    )
