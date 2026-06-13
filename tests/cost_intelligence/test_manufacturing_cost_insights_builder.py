import unittest


class TestManufacturingCostInsightsBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.manufacturing_cost_insights_builder import (
            ManufacturingCostInsightsBuilder,
        )

        self.builder = ManufacturingCostInsightsBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_no_insights_returns_low_risk(self):
        context = self._context()

        result = self.builder.build(context)

        self.assertEqual(result.insights, [])
        self.assertEqual(result.risk_level, "LOW")
        self.assertIs(result.warnings, context.warnings)

    def test_one_or_two_insights_returns_medium_risk(self):
        context = self._context(
            total_panels=51,
            total_edge_meters=101,
        )

        result = self.builder.build(context)

        self.assertEqual(
            result.insights,
            [
                "High panel count",
                "High edge banding usage",
            ],
        )
        self.assertEqual(result.risk_level, "MEDIUM")

    def test_three_or_more_insights_returns_high_risk(self):
        context = self._context(
            total_panels=51,
            total_edge_meters=101,
            total_drilling_operations=201,
            total_material_types=4,
            warnings_count=1,
            warnings=["Invalid panel width"],
        )

        result = self.builder.build(context)

        self.assertEqual(
            result.insights,
            [
                "High panel count",
                "High edge banding usage",
                "High drilling complexity",
                "Multiple material types",
                "Manufacturing warnings detected",
            ],
        )
        self.assertEqual(result.risk_level, "HIGH")
        self.assertIs(result.warnings, context.warnings)

    def test_threshold_values_do_not_add_insights(self):
        context = self._context(
            total_panels=50,
            total_edge_meters=100,
            total_drilling_operations=200,
            total_material_types=3,
            warnings_count=0,
        )

        result = self.builder.build(context)

        self.assertEqual(result.insights, [])
        self.assertEqual(result.risk_level, "LOW")

    @staticmethod
    def _context(**values):
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        return ManufacturingCostContext(**values)


if __name__ == "__main__":
    unittest.main()
