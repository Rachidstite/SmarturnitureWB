from project_engineering.operational_decision_report import OperationalDecisionReport
from project_engineering.project_engineering_readiness_report import (
    ProjectEngineeringReadinessReport,
)


def build_project_engineering_readiness_report(
    project_id: str,
    decision: OperationalDecisionReport,
) -> ProjectEngineeringReadinessReport:
    return ProjectEngineeringReadinessReport(
        project_id=project_id,
        ready_for_engineering_release=decision.ready_for_operation,
        ready_for_manufacturing_handoff=decision.ready_for_operation,
        blocking_violation_count=len(decision.violations),
        warning_count=len(decision.warnings),
        source="project-engineering-readiness-builder",
    )
