import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCostRiskReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from cost_intelligence.manufacturing_cost_risk_report import (
            ManufacturingCostRiskReport,
        )

        self.assertTrue(is_dataclass(ManufacturingCostRiskReport))

    def test_contract_has_required_fields(self):
        from cost_intelligence.manufacturing_cost_risk_report import (
            ManufacturingCostRiskReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCostRiskReport)],
            ["risk_level", "findings", "recommendation", "warnings"],
        )

    def test_contract_defaults(self):
        from cost_intelligence.manufacturing_cost_risk_report import (
            ManufacturingCostRiskReport,
        )

        report = ManufacturingCostRiskReport()

        self.assertEqual(report.risk_level, "LOW")
        self.assertEqual(report.findings, [])
        self.assertEqual(report.recommendation, "")
        self.assertEqual(report.warnings, [])

    def test_list_defaults_are_independent(self):
        from cost_intelligence.manufacturing_cost_risk_report import (
            ManufacturingCostRiskReport,
        )

        first_report = ManufacturingCostRiskReport()
        second_report = ManufacturingCostRiskReport()

        self.assertIsNot(first_report.findings, second_report.findings)
        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
