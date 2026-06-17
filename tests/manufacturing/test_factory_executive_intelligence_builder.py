import unittest


class TestFactoryExecutiveIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_executive_intelligence_builder import (
            FactoryExecutiveIntelligenceBuilder,
        )

        self.builder = FactoryExecutiveIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_report(self):
        from manufacturing.factory_executive_intelligence_report import (
            FactoryExecutiveIntelligenceReport,
        )

        report = self.builder.build(*self._inputs())

        self.assertIsInstance(report, FactoryExecutiveIntelligenceReport)

    def test_builder_maps_all_fields(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="LIMITED",
                load_status="HIGH",
                bottleneck="CNC",
                bottleneck_recommendation="Increase CNC availability",
                delivery_confidence="MEDIUM",
                delivery_risk="MEDIUM",
            )
        )

        self.assertEqual(report.capacity_status, "LIMITED")
        self.assertEqual(report.load_status, "HIGH")
        self.assertEqual(report.main_bottleneck, "CNC")
        self.assertEqual(report.delivery_confidence, "MEDIUM")
        self.assertEqual(report.delivery_risk, "MEDIUM")
        self.assertEqual(report.priority_action, "Increase CNC availability")
        self.assertEqual(report.factory_status, "ATTENTION_REQUIRED")
        self.assertIn("Factory needs attention", report.summary)

    def test_overloaded_capacity_forces_critical(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="OVERLOADED",
                load_status="LOW",
                delivery_confidence="HIGH",
                delivery_risk="LOW",
            )
        )

        self.assertEqual(report.factory_status, "CRITICAL")

    def test_high_delivery_risk_forces_critical(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="AVAILABLE",
                load_status="LOW",
                delivery_confidence="HIGH",
                delivery_risk="HIGH",
            )
        )

        self.assertEqual(report.factory_status, "CRITICAL")

    def test_stable_state_when_signals_are_clear(self):
        report = self.builder.build(
            *self._inputs(
                capacity_status="AVAILABLE",
                load_status="LOW",
                delivery_confidence="HIGH",
                delivery_risk="LOW",
            )
        )

        self.assertEqual(report.factory_status, "STABLE")
        self.assertIn("Factory is stable", report.summary)

    def test_builder_does_not_mutate_inputs(self):
        inputs = self._inputs()
        snapshots = [self._snapshot(report) for report in inputs]

        self.builder.build(*inputs)

        self.assertEqual([self._snapshot(report) for report in inputs], snapshots)

    @staticmethod
    def _snapshot(report):
        return dict(report.__dict__)

    @staticmethod
    def _inputs(
        capacity_status="AVAILABLE",
        load_status="LOW",
        bottleneck="",
        bottleneck_recommendation="No bottleneck detected",
        delivery_confidence="HIGH",
        delivery_risk="LOW",
    ):
        from manufacturing.delivery_intelligence_report import (
            DeliveryIntelligenceReport,
        )
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )
        from manufacturing.factory_capacity_intelligence_report import (
            FactoryCapacityIntelligenceReport,
        )
        from manufacturing.factory_load_report import FactoryLoadReport

        return (
            FactoryCapacityIntelligenceReport(status=capacity_status),
            FactoryLoadReport(
                status=load_status,
                bottleneck=bottleneck,
            ),
            FactoryBottleneckIntelligenceReport(
                bottleneck=bottleneck,
                recommendation=bottleneck_recommendation,
            ),
            DeliveryIntelligenceReport(
                confidence=delivery_confidence,
                delivery_risk=delivery_risk,
            ),
        )


if __name__ == "__main__":
    unittest.main()
