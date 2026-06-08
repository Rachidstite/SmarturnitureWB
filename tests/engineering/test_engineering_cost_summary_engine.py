from validation.intelligence.engineering.cost.engineering_cost_impact import (
    EngineeringCostImpact,
)

from validation.intelligence.engineering.cost.engineering_cost_summary_engine import (
    EngineeringCostSummaryEngine,
)


def test_cost_impacts_are_aggregated():

    impacts = [

        EngineeringCostImpact(
            code="A",
            material_sheets=0.10,
            machining_minutes=4,
            hardware_cost=20,
        ),

        EngineeringCostImpact(
            code="B",
            material_sheets=0.20,
            machining_minutes=6,
            hardware_cost=30,
        ),
    ]

    summary = (
        EngineeringCostSummaryEngine()
        .summarize(impacts)
    )

    assert summary.material_sheets == 0.30
    assert summary.machining_minutes == 10
    assert summary.hardware_cost == 50
