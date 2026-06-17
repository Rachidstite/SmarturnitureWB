import unittest


class TestAssemblyIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.assembly_intelligence_builder import (
            AssemblyIntelligenceBuilder,
        )

        self.builder = AssemblyIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_low_complexity(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        report = self.builder.build(
            JoineryIntelligenceReport(
                joinery_complexity_score=49,
                total_face_holes=10,
                total_edge_holes=5,
            )
        )

        self.assertEqual(report.assembly_time_minutes, 98)
        self.assertEqual(report.assembly_complexity, "LOW")
        self.assertEqual(report.required_installers, 1)
        self.assertEqual(report.joinery_density, 15)
        self.assertEqual(report.installation_risk, "LOW")

    def test_builder_medium_complexity(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        report = self.builder.build(
            JoineryIntelligenceReport(
                joinery_complexity_score=120,
                total_face_holes=20,
                total_edge_holes=10,
            )
        )

        self.assertEqual(report.assembly_time_minutes, 240)
        self.assertEqual(report.assembly_complexity, "MEDIUM")
        self.assertEqual(report.required_installers, 1)
        self.assertEqual(report.joinery_density, 30)
        self.assertEqual(report.installation_risk, "MEDIUM")

    def test_builder_high_complexity(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        report = self.builder.build(
            JoineryIntelligenceReport(
                joinery_complexity_score=121,
                total_face_holes=30,
                total_edge_holes=20,
            )
        )

        self.assertEqual(report.assembly_time_minutes, 242)
        self.assertEqual(report.assembly_complexity, "HIGH")
        self.assertEqual(report.required_installers, 2)
        self.assertEqual(report.joinery_density, 50)
        self.assertEqual(report.installation_risk, "HIGH")

    def test_builder_carries_warnings(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        report = self.builder.build(
            JoineryIntelligenceReport(
                joinery_complexity_score=0,
                total_face_holes=0,
                total_edge_holes=0,
                warnings=["joinery warning"],
            )
        )

        self.assertIn("joinery warning", report.warnings)
        self.assertIn("No assembly joinery detected", report.warnings)


if __name__ == "__main__":
    unittest.main()
