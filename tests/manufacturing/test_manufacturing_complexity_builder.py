import unittest


class TestManufacturingComplexityBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_complexity_builder import (
            ManufacturingComplexityBuilder,
        )

        self.builder = ManufacturingComplexityBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_prefers_joinery_complexity_score_when_available(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = self.builder.build(
            ManufacturingMetricsReport(
                total_panels=10,
                total_drilling_operations=30,
                total_edge_meters=20.0,
                total_material_types=1,
            ),
            joinery_report=JoineryIntelligenceReport(
                joinery_complexity_score=70,
            ),
        )

        self.assertEqual(report.engineering_complexity, "HIGH")
        self.assertEqual(report.estimated_engineering_minutes, 115.0)

    def test_builder_uses_metrics_fallback_when_joinery_is_missing(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = self.builder.build(
            ManufacturingMetricsReport(
                total_panels=12,
                total_drilling_operations=24,
                total_edge_meters=18.0,
                total_material_types=2,
            )
        )

        self.assertEqual(report.engineering_complexity, "LOW")
        self.assertEqual(report.estimated_engineering_minutes, 22.0)

    def test_builder_propagates_warnings(self):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        report = self.builder.build(
            ManufacturingMetricsReport(warnings=["Complexity warning"])
        )

        self.assertEqual(report.warnings, ["Complexity warning"])


if __name__ == "__main__":
    unittest.main()
