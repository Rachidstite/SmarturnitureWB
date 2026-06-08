from validation.intelligence.engineering.cost.engineering_cost_summary import (
    EngineeringCostSummary,
)

from validation.intelligence.engineering.cost.engineering_cost_estimator import (
    EngineeringCostEstimator,
)


def test_estimated_cost_is_computed():

    summary = EngineeringCostSummary(
        material_sheets=0.5,
        machining_minutes=10,
        hardware_cost=20,
    )

    cost = (
        EngineeringCostEstimator()
        .estimate(summary)
    )

    assert cost > 0
