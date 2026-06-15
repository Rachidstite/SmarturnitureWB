import unittest
from dataclasses import fields, is_dataclass


class TestFurnitureProjectSummaryContract(unittest.TestCase):

    def test_summary_is_dataclass_with_exact_field_order(self):
        from manufacturing.furniture_project_summary import FurnitureProjectSummary

        self.assertTrue(is_dataclass(FurnitureProjectSummary))
        self.assertEqual(
            [field.name for field in fields(FurnitureProjectSummary)],
            [
                "total_cabinets",
                "total_physical_parts",
                "total_machining_operations",
            ],
        )

    def test_summary_has_safe_defaults(self):
        from manufacturing.furniture_project_summary import FurnitureProjectSummary

        summary = FurnitureProjectSummary()

        self.assertEqual(summary.total_cabinets, 0)
        self.assertEqual(summary.total_physical_parts, 0)
        self.assertEqual(summary.total_machining_operations, 0)


if __name__ == "__main__":
    unittest.main()
