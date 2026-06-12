import unittest
from dataclasses import fields

from exports.strategies import SheetResult
from validation.intelligence.engineering.cost.engineering_cost_estimator import (
    EngineeringCostEstimator,
)
from validation.intelligence.engineering.cost.engineering_cost_summary import (
    EngineeringCostSummary,
)


class TestSheetCostCharacterization(unittest.TestCase):

    def test_engineering_estimator_uses_a_fixed_fractional_sheet_rate(self):
        summary = EngineeringCostSummary(
            material_sheets=0.5,
            machining_minutes=0,
            hardware_cost=0,
        )

        self.assertEqual(EngineeringCostEstimator().estimate(summary), 400.0)
        self.assertEqual(EngineeringCostEstimator.MDF_SHEET_COST, 800)

    def test_nesting_sheet_result_separates_geometry_from_cost_metadata(self):
        field_names = {field.name for field in fields(SheetResult)}

        self.assertIn("sheet_id", field_names)
        self.assertIn("used_area", field_names)
        self.assertIn("sheet_width", field_names)
        self.assertIn("sheet_height", field_names)
        self.assertIn("kerf", field_names)
        self.assertIn("trim", field_names)
        self.assertIn("material", field_names)
        self.assertIn("thickness", field_names)
        self.assertNotIn("sheet_cost", field_names)


if __name__ == "__main__":
    unittest.main()
