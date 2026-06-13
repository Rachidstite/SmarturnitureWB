import unittest


class TestManufacturingSummaryBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_summary_builder import (
            ManufacturingSummaryBuilder,
        )

        self.assertTrue(callable(ManufacturingSummaryBuilder().build))

    def test_build_returns_summary_for_package(self):
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.manufacturing_summary_builder import (
            ManufacturingSummaryBuilder,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        package = ManufacturingPackage(
            panels=[object(), object()],
            materials=[object()],
            edge_operations=[object(), object(), object()],
            machining_operations=[object()],
            warnings=["Missing edge data"],
        )

        report = ManufacturingSummaryBuilder().build(package)

        self.assertIsInstance(report, ManufacturingSummaryReport)
        self.assertEqual(report.total_panels, 2)
        self.assertEqual(report.total_materials, 1)
        self.assertEqual(report.total_edge_operations, 3)
        self.assertEqual(report.total_machining_operations, 1)
        self.assertIs(report.warnings, package.warnings)


if __name__ == "__main__":
    unittest.main()
