from validation.intelligence.engineering.cost.engineering_cost_engine import (
    EngineeringCostEngine,
)


def test_shelf_deflection_has_cost_impact():

    impacts = (
        EngineeringCostEngine()
        .calculate(
            [
                "SHELF_DEFLECTION",
            ]
        )
    )

    assert len(impacts) == 1

    assert (
        impacts[0].material_sheets
        > 0
    )
