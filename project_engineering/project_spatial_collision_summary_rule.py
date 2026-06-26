from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.project_spatial_summary_report import (
    ProjectSpatialSummaryReport,
)


def evaluate_project_spatial_collision_summary(
    report: ProjectSpatialSummaryReport,
    rule_id: str = "PROJECT_SPATIAL_COLLISION_SUMMARY",
    source: str = "project-spatial-collision-summary-rule",
) -> OperationalRuleResult:
    if not report.has_collisions:
        return OperationalRuleResult(
            rule_id=rule_id,
            capability="project_spatial_collision",
            component_id=report.project_id,
            passed=True,
            severity="info",
            message="",
            source=source,
        )

    return OperationalRuleResult(
        rule_id=rule_id,
        capability="project_spatial_collision",
        component_id=report.project_id,
        passed=False,
        severity="error",
        message=(
            "Project spatial collisions detected for "
            f"project_id={report.project_id} with collision_count={report.collision_count}"
        ),
        source=source,
    )
