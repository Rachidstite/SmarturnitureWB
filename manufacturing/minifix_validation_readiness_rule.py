from manufacturing.minifix_validation_report import MinifixValidationReport
from project_engineering.operational_rule_result import OperationalRuleResult


RULE_ID = "MANUFACTURING_MINIFIX_VALIDATION_READINESS"
CAPABILITY = "manufacturing_minifix_validation_readiness"
COMPONENT_ID = "minifix-validation"
SOURCE = "minifix-validation-readiness-rule"


def evaluate_minifix_validation_readiness(
    report: MinifixValidationReport,
) -> OperationalRuleResult:
    ready_status = str(getattr(report, "validation_status", "")).strip().upper()
    ready = bool(report.is_valid) or ready_status in {
        "READY",
        "VALID",
        "PASS",
        "PASSED",
    }

    if ready:
        return OperationalRuleResult(
            rule_id=RULE_ID,
            capability=CAPABILITY,
            component_id=COMPONENT_ID,
            passed=True,
            severity="info",
            message="",
            source=SOURCE,
        )

    return OperationalRuleResult(
        rule_id=RULE_ID,
        capability=CAPABILITY,
        component_id=COMPONENT_ID,
        passed=False,
        severity="error",
        message=(
            "Minifix validation readiness failed: "
            f"is_valid={report.is_valid}, "
            f"validation_status={report.validation_status}, "
            f"edge_distance_risk={report.edge_distance_risk}, "
            f"panel_thickness_risk={report.panel_thickness_risk}, "
            f"spacing_risk={report.spacing_risk}, "
            f"cam_lock_risk={report.cam_lock_risk}, "
            f"dowel_support_risk={report.dowel_support_risk}, "
            f"assembly_risk={report.assembly_risk}, "
            f"manufacturing_warning={report.manufacturing_warning}, "
            f"recommended_action={report.recommended_action}"
        ),
        source=SOURCE,
    )
