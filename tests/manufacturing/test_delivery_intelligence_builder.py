import unittest


class TestDeliveryIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.delivery_intelligence_builder import (
            DeliveryIntelligenceBuilder,
        )

        self.builder = DeliveryIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_report(self):
        from manufacturing.delivery_intelligence_report import (
            DeliveryIntelligenceReport,
        )

        report = self.builder.build(*self._inputs())

        self.assertIsInstance(report, DeliveryIntelligenceReport)

    def test_available_capacity_and_low_bottleneck_give_high_confidence(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="AVAILABLE",
                bottleneck_severity="LOW",
            )
        )

        self.assertEqual(report.confidence, "HIGH")
        self.assertEqual(report.delivery_risk, "LOW")

    def test_limited_capacity_gives_medium_confidence(self):
        report = self.builder.build(
            *self._inputs(capacity_status="LIMITED", bottleneck_severity="LOW")
        )

        self.assertEqual(report.confidence, "MEDIUM")
        self.assertEqual(report.delivery_risk, "MEDIUM")

    def test_overloaded_capacity_gives_low_confidence(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="OVERLOADED",
                bottleneck_severity="LOW",
            )
        )

        self.assertEqual(report.confidence, "LOW")
        self.assertEqual(report.delivery_risk, "HIGH")

    def test_high_bottleneck_severity_gives_low_confidence(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="AVAILABLE",
                bottleneck_severity="HIGH",
            )
        )

        self.assertEqual(report.confidence, "LOW")
        self.assertEqual(report.delivery_risk, "HIGH")

    def test_builder_uses_duration_hours_and_days(self):
        report = self.builder.build(
            *self._inputs(total_production_minutes=960.0)
        )

        self.assertEqual(report.estimated_hours, 16.0)
        self.assertEqual(report.estimated_days, 2.0)

    def test_builder_does_not_mutate_inputs(self):
        inputs = self._inputs()
        snapshots = [self._snapshot(report) for report in inputs]

        self.builder.build(*inputs)

        self.assertEqual([self._snapshot(report) for report in inputs], snapshots)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _inputs(
        total_production_minutes=480.0,
        capacity_status="AVAILABLE",
        bottleneck_severity="LOW",
    ):
        from manufacturing.delivery_intelligence_builder import (
            DeliveryIntelligenceBuilder,
        )
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )
        from manufacturing.factory_capacity_intelligence_report import (
            FactoryCapacityIntelligenceReport,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        return (
            ManufacturingDurationReport(
                total_production_minutes=total_production_minutes,
            ),
            FactoryCapacityIntelligenceReport(status=capacity_status),
            FactoryBottleneckIntelligenceReport(severity=bottleneck_severity),
        )


if __name__ == "__main__":
    unittest.main()
