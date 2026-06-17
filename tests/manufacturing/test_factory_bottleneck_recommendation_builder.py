import unittest


class TestFactoryBottleneckRecommendationBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_bottleneck_recommendation_builder import (
            FactoryBottleneckRecommendationBuilder,
        )

        self.builder = FactoryBottleneckRecommendationBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_assembly_recommendations(self):
        report = self.builder.build(self._input(bottleneck="ASSEMBLY"))

        self.assertEqual(report.primary_recommendation, "Increase assembly capacity")
        self.assertEqual(
            report.secondary_recommendations,
            [
                "Add assembly station",
                "Split project into smaller batches",
                "Reduce assembly minutes per panel",
            ],
        )
        self.assertEqual(report.expected_impact, "Improves delivery reliability")

    def test_cnc_recommendations(self):
        report = self.builder.build(self._input(bottleneck="CNC"))

        self.assertEqual(report.primary_recommendation, "Increase CNC availability")
        self.assertEqual(
            report.secondary_recommendations,
            [
                "Schedule CNC work earlier",
                "Reduce unnecessary drilling operations",
                "Batch similar CNC operations",
            ],
        )
        self.assertEqual(
            report.expected_impact, "Reduces machining queue pressure"
        )

    def test_edge_banding_recommendations(self):
        report = self.builder.build(self._input(bottleneck="EDGE_BANDING"))

        self.assertEqual(
            report.primary_recommendation,
            "Increase edge banding capacity",
        )
        self.assertEqual(
            report.secondary_recommendations,
            [
                "Batch panels by edge material",
                "Prepare edge rolls before production",
                "Reduce unnecessary edge banding",
            ],
        )
        self.assertEqual(report.expected_impact, "Reduces finishing delays")

    def test_unknown_recommendations(self):
        report = self.builder.build(self._input(bottleneck=""))

        self.assertEqual(report.primary_recommendation, "No bottleneck detected")
        self.assertEqual(report.secondary_recommendations, [])
        self.assertEqual(
            report.expected_impact, "No immediate action required"
        )

    def test_builder_does_not_mutate_inputs(self):
        input_report = self._input(bottleneck="CNC", severity="HIGH")
        snapshot = dict(input_report.__dict__)

        self.builder.build(input_report)

        self.assertEqual(input_report.__dict__, snapshot)

    @staticmethod
    def _input(bottleneck="CNC", severity="HIGH"):
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        return FactoryBottleneckIntelligenceReport(
            bottleneck=bottleneck,
            severity=severity,
        )


if __name__ == "__main__":
    unittest.main()
