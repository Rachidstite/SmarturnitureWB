from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.project_collision_fact import ProjectCollisionFact


def evaluate_project_static_collision(
    collision: ProjectCollisionFact,
    rule_id: str = "PROJECT_STATIC_COLLISION",
    source: str = "project-static-collision-rule",
) -> OperationalRuleResult:
    message = (
        "Static collision detected between "
        f"{collision.first_component_id} and {collision.second_component_id}"
    )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="project_static_collision",
        component_id=collision.first_component_id,
        passed=False,
        severity=collision.severity if collision.severity == "warning" else "error",
        message=message,
        source=source,
    )
