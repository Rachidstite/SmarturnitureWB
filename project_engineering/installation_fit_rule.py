from project_engineering.installation_area_fact import InstallationAreaFact
from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.project_footprint import ProjectFootprint


def evaluate_installation_fit(
    footprint: ProjectFootprint,
    installation_area: InstallationAreaFact,
) -> OperationalRuleResult:
    if (
        footprint.x_min >= installation_area.x_min
        and footprint.y_min >= installation_area.y_min
        and footprint.x_max <= installation_area.x_max
        and footprint.y_max <= installation_area.y_max
    ):
        return OperationalRuleResult(
            rule_id="INSTALLATION_FIT",
            capability="installation_fit",
            component_id=installation_area.area_id,
            passed=True,
            severity="info",
            message="",
            source="",
        )

    return OperationalRuleResult(
        rule_id="INSTALLATION_FIT",
        capability="installation_fit",
        component_id=installation_area.area_id,
        passed=False,
        severity="error",
        message=(
            "Project footprint exceeds installation area: "
            f"footprint=({footprint.x_min}, {footprint.y_min}, {footprint.x_max}, {footprint.y_max}), "
            f"area=({installation_area.x_min}, {installation_area.y_min}, {installation_area.x_max}, {installation_area.y_max})"
        ),
        source="",
    )
