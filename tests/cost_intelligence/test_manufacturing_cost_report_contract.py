import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCostReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        self.assertTrue(is_dataclass(ManufacturingCostReport))

    def test_contract_has_required_fields(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCostReport)],
            [
                "material_cost",
                "edge_banding_cost",
                "drilling_cost",
                "hardware_cost",
                "complexity_cost",
                "panel_handling_cost",
                "cnc_labor_cost",
                "drilling_labor_cost",
                "edge_banding_labor_cost",
                "assembly_labor_cost",
                "total_labor_cost",
                "overhead_cost",
                "total_manufacturing_cost",
                "currency",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        report = ManufacturingCostReport()

        self.assertEqual(report.material_cost, 0.0)
        self.assertEqual(report.edge_banding_cost, 0.0)
        self.assertEqual(report.drilling_cost, 0.0)
        self.assertEqual(report.hardware_cost, 0.0)
        self.assertEqual(report.complexity_cost, 0.0)
        self.assertEqual(report.panel_handling_cost, 0.0)
        self.assertEqual(report.cnc_labor_cost, 0.0)
        self.assertEqual(report.drilling_labor_cost, 0.0)
        self.assertEqual(report.edge_banding_labor_cost, 0.0)
        self.assertEqual(report.assembly_labor_cost, 0.0)
        self.assertEqual(report.total_labor_cost, 0.0)
        self.assertEqual(report.overhead_cost, 0.0)
        self.assertEqual(report.total_manufacturing_cost, 0.0)
        self.assertEqual(report.currency, "MAD")
        self.assertEqual(report.warnings, [])

    def test_warning_defaults_are_independent(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        first_report = ManufacturingCostReport()
        second_report = ManufacturingCostReport()

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
