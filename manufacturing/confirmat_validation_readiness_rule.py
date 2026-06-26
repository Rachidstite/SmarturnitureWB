from manufacturing.confirmat_validation_report import ConfirmatValidationReport
from project_engineering.operational_rule_result import OperationalRuleResult


RULE_ID = "MANUFACTURING_CONFIRMAT_VALIDATION_READINESS"
CAPABILITY = "manufacturing_confirmat_validation_readiness"
COMPONENT_ID = "confirmat-validation"
SOURCE = "confirmat-validation-readiness-rule"


def evaluate_confirmat_validation_readiness(
    report: ConfirmatValidationReport,
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
            "Confirmat validation readiness failed: "
            f"validation_status={report.validation_status}, "
            f"is_valid={report.is_valid}, "
            f"edge_distance_risk={report.edge_distance_risk}, "
            f"spacing_risk={report.spacing_risk}, "
            f"assembly_risk={report.assembly_risk}, "
            f"manufacturing_warning={report.manufacturing_warning}, "
            f"recommended_action={report.recommended_action}"
        ),
        source=SOURCE,
    )
