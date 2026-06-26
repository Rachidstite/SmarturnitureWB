from manufacturing.drawer_validation_report import DrawerValidationReport
from project_engineering.operational_rule_result import OperationalRuleResult


RULE_ID = "MANUFACTURING_DRAWER_SLIDE_VALIDATION_READINESS"
CAPABILITY = "manufacturing_drawer_slide_validation_readiness"
COMPONENT_ID = "drawer-slide-validation"
SOURCE = "drawer-slide-validation-readiness-rule"


def evaluate_drawer_slide_validation_readiness(
    report: DrawerValidationReport,
) -> OperationalRuleResult:
    ready = (
        report.drawer_width > 0
        and report.drawer_depth > 0
        and report.slide_length > 0
        and report.hardware_complete is True
    )

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
            "Drawer slide validation readiness failed: "
            f"drawer_width={report.drawer_width}, "
            f"drawer_depth={report.drawer_depth}, "
            f"slide_length={report.slide_length}, "
            f"hardware_complete={report.hardware_complete}"
        ),
        source=SOURCE,
    )
