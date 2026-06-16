import unittest


class TestManufacturingWasteCostBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_waste_cost_builder import (
            ManufacturingWasteCostBuilder,
        )

        self.assertTrue(callable(ManufacturingWasteCostBuilder().build))

    def test_zero_waste_results_in_zero_cost(self):
        from manufacturing.manufacturing_waste_cost_builder import (
            ManufacturingWasteCostBuilder,
        )
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        report = ManufacturingWasteCostBuilder().build(
            SheetUtilizationReport(waste_area_m2=0.0)
        )

        self.assertEqual(report.waste_area_m2, 0.0)
        self.assertEqual(report.estimated_waste_cost, 0.0)
        self.assertEqual(report.sheet_cost, 800.0)
        self.assertEqual(report.warnings, [])

    def test_one_square_meter_waste_uses_expected_cost(self):
        from manufacturing.manufacturing_waste_cost_builder import (
            ManufacturingWasteCostBuilder,
        )
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        report = ManufacturingWasteCostBuilder().build(
            SheetUtilizationReport(waste_area_m2=1.0)
        )

        self.assertAlmostEqual(
            report.estimated_waste_cost,
            800.0 / 5.796,
            places=10,
        )
        self.assertEqual(report.sheet_cost, 800.0)

    def test_builder_propagates_warnings_without_mutating_input(self):
        from manufacturing.manufacturing_waste_cost_builder import (
            ManufacturingWasteCostBuilder,
        )
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        sheet_report = SheetUtilizationReport(
            waste_area_m2=2.0,
            warnings=["Sheet warning"],
        )

        report = ManufacturingWasteCostBuilder().build(sheet_report)

        self.assertEqual(report.warnings, ["Sheet warning"])
        self.assertEqual(sheet_report.warnings, ["Sheet warning"])
        self.assertIsNot(report.warnings, sheet_report.warnings)


if __name__ == "__main__":
    unittest.main()
