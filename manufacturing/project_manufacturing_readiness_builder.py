from manufacturing.project_manufacturing_readiness_report import (
    ProjectManufacturingReadinessReport,
)
from project_engineering.project_engineering_readiness_report import (
    ProjectEngineeringReadinessReport,
)


class ProjectManufacturingReadinessBuilder:

    def build(
        self,
        cabinet_structural_report=None,
        cabinet_stability_report=None,
        hardware_placement_report=None,
        kitchen_manufacturing_report=None,
        engineering_readiness_report=None,
    ):
        if engineering_readiness_report is not None:
            if engineering_readiness_report.ready_for_manufacturing_handoff:
                return ProjectManufacturingReadinessReport(
                    readiness_status="READY",
                    structural_risk="LOW",
                    engineering_review_required=False,
                    manufacturing_recommendation=(
                        "Project is ready for manufacturing handoff. "
                        "engineering handoff ready."
                    ),
                )

            return ProjectManufacturingReadinessReport(
                readiness_status="BLOCKED",
                structural_risk="HIGH",
                engineering_review_required=True,
                manufacturing_recommendation=(
                    "engineering handoff blocked: "
                    f"blocking_violation_count={engineering_readiness_report.blocking_violation_count}, "
                    f"warning_count={engineering_readiness_report.warning_count}"
                ),
            )

        severities = [
            getattr(cabinet_structural_report, "structural_risk", "LOW"),
            getattr(cabinet_structural_report, "stability_risk", "LOW"),
            getattr(cabinet_stability_report, "tipping_risk", "LOW"),
            getattr(cabinet_stability_report, "large_span_risk", "LOW"),
            getattr(hardware_placement_report, "hardware_risk", "LOW"),
            getattr(kitchen_manufacturing_report, "manufacturing_complexity", "LOW"),
        ]

        if "HIGH" in severities:
            readiness_status = "BLOCKED"
            engineering_review_required = True
            manufacturing_recommendation = "Project manufacturing review required"
            structural_risk = "HIGH"
        elif getattr(kitchen_manufacturing_report, "cabinet_count", 0) >= 2:
            readiness_status = "REVIEW"
            engineering_review_required = True
            manufacturing_recommendation = (
                "Multi-cabinet project requires installation review"
            )
            structural_risk = "LOW"
        elif "MEDIUM" in severities:
            readiness_status = "REVIEW"
            engineering_review_required = False
            manufacturing_recommendation = "Project should be reviewed before production"
            structural_risk = "MEDIUM"
        else:
            readiness_status = "READY"
            engineering_review_required = False
            manufacturing_recommendation = ""
            structural_risk = "LOW"

        return ProjectManufacturingReadinessReport(
            readiness_status=readiness_status,
            structural_risk=structural_risk,
            engineering_review_required=engineering_review_required,
            manufacturing_recommendation=manufacturing_recommendation,
        )
