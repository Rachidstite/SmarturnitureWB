import unittest
from dataclasses import fields, is_dataclass


class TestFactoryLoadReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.factory_load_report import FactoryLoadReport

        self.assertTrue(is_dataclass(FactoryLoadReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.factory_load_report import FactoryLoadReport

        self.assertEqual(
            [field.name for field in fields(FactoryLoadReport)],
            [
                "cnc_load_percent",
                "assembly_load_percent",
                "edge_banding_load_percent",
                "bottleneck",
                "status",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_load_report import FactoryLoadReport

        report = FactoryLoadReport()

        self.assertEqual(report.cnc_load_percent, 0.0)
        self.assertEqual(report.assembly_load_percent, 0.0)
        self.assertEqual(report.edge_banding_load_percent, 0.0)
        self.assertEqual(report.bottleneck, "")
        self.assertEqual(report.status, "LOW")


if __name__ == "__main__":
    unittest.main()
