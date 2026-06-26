from manufacturing.door_engineering_report import DoorEngineeringReport
from project_engineering.operational_rule_result import OperationalRuleResult


def evaluate_door_hinge_engineering_readiness(
    report: DoorEngineeringReport,
    rule_id: str = "MANUFACTURING_DOOR_HINGE_ENGINEERING_READINESS",
    source: str = "door-hinge-engineering-readiness-rule",
) -> OperationalRuleResult:
    if report.hinge_requirement and report.recommended_hinge_count > 0:
        return OperationalRuleResult(
            rule_id=rule_id,
            capability="manufacturing_door_hinge_engineering_readiness",
            component_id="door-hinge-engineering",
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="manufacturing_door_hinge_engineering_readiness",
        component_id="door-hinge-engineering",
        passed=False,
        severity="error",
        message=(
            "Door hinge engineering readiness failed: "
            f"hinge_requirement={report.hinge_requirement}, "
            f"recommended_hinge_count={report.recommended_hinge_count}"
        ),
        source=source,
    )
