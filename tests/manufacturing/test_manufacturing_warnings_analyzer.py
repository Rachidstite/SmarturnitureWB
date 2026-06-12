import unittest


class TestManufacturingWarningsAnalyzer(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_warnings_analyzer import (
            ManufacturingWarningsAnalyzer,
        )

        self.analyzer = ManufacturingWarningsAnalyzer()

    def test_analyzer_exists(self):
        self.assertTrue(callable(self.analyzer.analyze))

    def test_empty_package_returns_all_warnings(self):
        from manufacturing.manufacturing_package import ManufacturingPackage

        warnings = self.analyzer.analyze(ManufacturingPackage())

        self.assertEqual(
            warnings,
            [
                "No panels",
                "No materials",
                "No machining operations",
                "No edge operations",
            ],
        )
        self.assertTrue(all(isinstance(warning, str) for warning in warnings))

    def test_no_panels_warning(self):
        package = self._populated_package()
        package.panels = []

        self.assertEqual(self.analyzer.analyze(package), ["No panels"])

    def test_no_materials_warning(self):
        package = self._populated_package()
        package.materials = []

        self.assertEqual(self.analyzer.analyze(package), ["No materials"])

    def test_no_machining_operations_warning(self):
        package = self._populated_package()
        package.machining_operations = []

        self.assertEqual(
            self.analyzer.analyze(package),
            ["No machining operations"],
        )

    def test_no_edge_operations_warning(self):
        package = self._populated_package()
        package.edge_operations = []

        self.assertEqual(self.analyzer.analyze(package), ["No edge operations"])

    def test_populated_package_returns_no_warnings(self):
        self.assertEqual(self.analyzer.analyze(self._populated_package()), [])

    @staticmethod
    def _populated_package():
        from manufacturing.manufacturing_package import ManufacturingPackage

        return ManufacturingPackage(
            panels=[object()],
            materials=[object()],
            machining_operations=[object()],
            edge_operations=[object()],
        )


if __name__ == "__main__":
    unittest.main()
