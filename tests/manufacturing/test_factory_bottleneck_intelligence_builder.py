import unittest
from dataclasses import dataclass


@dataclass
class _ProductionScheduleReport:
    schedule_risk_level: str = "LOW"
    warnings: list = None


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

    def test_high_schedule_risk_escalates_low_load_severity(self):
        report = self.builder.build(
            self._load_report(status="LOW", bottleneck="CNC"),
            _ProductionScheduleReport(schedule_risk_level="HIGH"),
        )

        self.assertEqual(report.severity, "MEDIUM")
        self.assertEqual(report.impact, "CAPACITY_PRESSURE")
        self.assertIn("review production schedule", report.recommendation)

    def test_high_schedule_risk_escalates_medium_load_to_delivery_risk(self):
        report = self.builder.build(
            self._load_report(status="MEDIUM", bottleneck="ASSEMBLY"),
            _ProductionScheduleReport(schedule_risk_level="HIGH"),
        )

        self.assertEqual(report.severity, "HIGH")
        self.assertEqual(report.impact, "DELIVERY_RISK")
        self.assertIn("review production schedule", report.recommendation)

    def test_medium_schedule_risk_does_not_change_load_based_mapping(self):
        report = self.builder.build(
            self._load_report(status="LOW", bottleneck="EDGE_BANDING"),
            _ProductionScheduleReport(schedule_risk_level="MEDIUM"),
        )

        self.assertEqual(report.severity, "LOW")
        self.assertEqual(report.impact, "NO_MAJOR_BOTTLENECK")
        self.assertEqual(
            report.recommendation,
            "Increase edge banding capacity",
        )

    def test_builder_handles_unknown_bottleneck(self):
        report = self.builder.build(
            self._load_report(bottleneck=""),
            _ProductionScheduleReport(schedule_risk_level="HIGH"),
        )

        self.assertEqual(report.load_percent, 0.0)
        self.assertEqual(report.recommendation, "No bottleneck detected")

    def test_builder_does_not_mutate_input(self):
        load_report = self._load_report(bottleneck="CNC", status="HIGH")
        snapshot = self._snapshot(load_report)
        schedule_report = _ProductionScheduleReport(
            schedule_risk_level="HIGH",
            warnings=["schedule-warning"],
        )
        schedule_snapshot = self._snapshot(schedule_report)

        self.builder.build(load_report, schedule_report)

        self.assertEqual(self._snapshot(load_report), snapshot)
        self.assertEqual(self._snapshot(schedule_report), schedule_snapshot)

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
