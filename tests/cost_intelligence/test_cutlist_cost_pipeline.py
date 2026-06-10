import unittest
from dataclasses import fields

from exports.cutlist_engine import CutListItem
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy, SheetResult
from validation.intelligence.engineering.cost.engineering_cost_estimator import (
    EngineeringCostEstimator,
)
from validation.intelligence.engineering.cost.engineering_cost_summary import (
    EngineeringCostSummary,
)
from validation.intelligence.unused_operation_cost_impact import (
    UnusedOperationCostImpact,
)


class TestCutlistCostPipelineCharacterization(unittest.TestCase):

    def test_cutlist_to_nesting_pipeline_carries_no_cost_fields(self):
        item = CutListItem(
            identity="P1",
            width=100,
            height=50,
            thickness=18,
            material="MDF",
            group="CARCASS",
            role="SIDE",
        )

        result = IndustrialNestingEngine(
            GuillotineStripStrategy(),
            sheet_width=300,
            sheet_height=200,
        ).process([item])

        self.assertEqual(list(result), ["MDF_18MM"])
        self.assertEqual(len(result["MDF_18MM"]), 1)

        cutlist_fields = {field.name for field in fields(CutListItem)}
        sheet_fields = {field.name for field in fields(SheetResult)}
        self.assertFalse(
            {"unit_cost", "material_cost", "manufacturing_cost"} & cutlist_fields
        )
        self.assertFalse(
            {"sheet_cost", "waste_cost", "manufacturing_cost"} & sheet_fields
        )

    def test_manufacturing_cost_concepts_use_independent_fixed_amounts(self):
        panel = type(
            "Panel",
            (),
            {
                "unified_operations": [
                    type("Operation", (), {"metadata": {}})(),
                ],
            },
        )()

        savings = UnusedOperationCostImpact().estimate([panel])
        manufacturing_estimate = EngineeringCostEstimator().estimate(
            EngineeringCostSummary(
                material_sheets=0,
                machining_minutes=1,
                hardware_cost=0,
            )
        )

        self.assertEqual(savings[0].estimated_savings, 1.0)
        self.assertEqual(manufacturing_estimate, 2)
        self.assertFalse(hasattr(savings[0], "currency"))


if __name__ == "__main__":
    unittest.main()
