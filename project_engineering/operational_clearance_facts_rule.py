from project_engineering.available_operational_clearance_fact import (
    AvailableOperationalClearanceFact,
)
from project_engineering.operational_clearance_distance_rule import (
    evaluate_operational_clearance_distance,
)
from project_engineering.operational_rule_result import OperationalRuleResult
from project_engineering.required_operational_clearance_fact import (
    RequiredOperationalClearanceFact,
)


def evaluate_operational_clearance_facts(
    available_fact: AvailableOperationalClearanceFact,
    required_fact: RequiredOperationalClearanceFact,
    rule_id: str = "OPERATIONAL_CLEARANCE_DISTANCE",
    source: str = "",
) -> OperationalRuleResult:
    return evaluate_operational_clearance_distance(
        component_id=available_fact.component_id,
        available_clearance_mm=available_fact.available_clearance_mm,
        required_clearance_mm=required_fact.required_clearance_mm,
        capability="operational_clearance",
        rule_id=rule_id,
        source=source,
    )
