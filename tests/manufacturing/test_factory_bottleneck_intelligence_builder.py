import unittest


class TestFactoryBottleneckIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_bottleneck_intelligence_builder import (
            FactoryBottleneckIntelligenceBuilder,
        )

        self.builder = FactoryBottleneckIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_report(self):
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        report = self.builder.build(self._load_report())

        self.assertIsInstance(report, FactoryBottleneckIntelligenceReport)

    def test_builder_maps_cnc_bottleneck(self):
        report = self.builder.build(self._load_report(bottleneck="CNC"))

        self.assertEqual(report.bottleneck, "CNC")
        self.assertEqual(report.load_percent, 72.5)
        self.assertEqual(report.recommendation, "Increase CNC availability")

    def test_builder_maps_assembly_bottleneck(self):
        report = self.builder.build(self._load_report(bottleneck="ASSEMBLY"))

        self.assertEqual(report.bottleneck, "ASSEMBLY")
        self.assertEqual(report.load_percent, 81.0)
        self.assertEqual(report.recommendation, "Increase assembly capacity")

    def test_builder_maps_edge_banding_bottleneck(self):
        report = self.builder.build(self._load_report(bottleneck="EDGE_BANDING"))

        self.assertEqual(report.bottleneck, "EDGE_BANDING")
        self.assertEqual(report.load_percent, 33.0)
        self.assertEqual(
            report.recommendation, "Increase edge banding capacity"
        )

    def test_builder_maps_severity_and_impact_from_status(self):
        high_report = self.builder.build(self._load_report(status="HIGH"))
        medium_report = self.builder.build(self._load_report(status="MEDIUM"))
        low_report = self.builder.build(self._load_report(status="LOW"))

        self.assertEqual(high_report.severity, "HIGH")
        self.assertEqual(high_report.impact, "DELIVERY_RISK")
        self.assertEqual(medium_report.severity, "MEDIUM")
        self.assertEqual(medium_report.impact, "CAPACITY_PRESSURE")
        self.assertEqual(low_report.severity, "LOW")
        self.assertEqual(low_report.impact, "NO_MAJOR_BOTTLENECK")

    def test_builder_handles_unknown_bottleneck(self):
        report = self.builder.build(self._load_report(bottleneck=""))

        self.assertEqual(report.load_percent, 0.0)
        self.assertEqual(report.recommendation, "No bottleneck detected")

    def test_builder_does_not_mutate_input(self):
        load_report = self._load_report(bottleneck="CNC", status="HIGH")
        snapshot = self._snapshot(load_report)

        self.builder.build(load_report)

        self.assertEqual(self._snapshot(load_report), snapshot)

    @staticmethod
    def _snapshot(report):
        return dict(report.__dict__)

    @staticmethod
    def _load_report(bottleneck="CNC", status="LOW"):
        from manufacturing.factory_load_report import FactoryLoadReport

        return FactoryLoadReport(
            cnc_load_percent=72.5,
            assembly_load_percent=81.0,
            edge_banding_load_percent=33.0,
            bottleneck=bottleneck,
            status=status,
        )


if __name__ == "__main__":
    unittest.main()
