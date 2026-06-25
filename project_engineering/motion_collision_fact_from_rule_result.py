from project_engineering.motion_collision_fact import MotionCollisionFact
from project_engineering.operational_rule_result import OperationalRuleResult


def build_motion_collision_fact_from_rule_result(
    result: OperationalRuleResult,
    obstacle_component_id: str,
    collision_type: str = "aabb_overlap",
) -> MotionCollisionFact:
    if result.passed:
        return MotionCollisionFact(
            moving_component_id=result.component_id,
            obstacle_component_id=obstacle_component_id,
            collision_type="",
            severity="info",
            message="",
            source=result.source,
        )

    return MotionCollisionFact(
        moving_component_id=result.component_id,
        obstacle_component_id=obstacle_component_id,
        collision_type=collision_type,
        severity=result.severity,
        message=result.message,
        source=result.source,
    )
