import unittest


class TestHardwarePlacementBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.hardware_placement_builder import (
            HardwarePlacementBuilder,
        )

        self.builder = HardwarePlacementBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_hardware_placement_report(self):
        from manufacturing.hardware_placement_report import (
            HardwarePlacementReport,
        )

        report = self.builder.build()

        self.assertIsInstance(report, HardwarePlacementReport)

    def test_all_reports_missing_sets_high_risk(self):
        report = self.builder.build()

        self.assertEqual(report.hardware_risk, "HIGH")
        self.assertEqual(report.hardware_recommendation, "Hardware engineering review required")

    def test_invalid_validation_sets_high_risk(self):
        report = self.builder.build(
            self._minifix_report(is_valid=False),
            self._confirmat_report(is_valid=True),
            self._hinge_report(),
        )

        self.assertEqual(report.hardware_risk, "HIGH")

    def test_review_required_sets_medium_risk(self):
        report = self.builder.build(
            self._minifix_report(is_valid=True, requires_review=True),
            self._confirmat_report(is_valid=True),
            self._hinge_report(),
        )

        self.assertEqual(report.hardware_risk, "MEDIUM")
        self.assertEqual(
            report.hardware_recommendation,
            "Hardware placement review recommended",
        )

    def test_low_risk_sets_low_hardware_risk(self):
        report = self.builder.build(
            self._minifix_report(is_valid=True),
            self._confirmat_report(is_valid=True),
            self._hinge_report(),
        )

        self.assertEqual(report.hardware_risk, "LOW")
        self.assertEqual(report.hardware_recommendation, "")

    def test_low_risk_placement_quality_and_coverage(self):
        report = self.builder.build(
            self._minifix_report(is_valid=True),
            self._confirmat_report(is_valid=True),
            self._hinge_report(),
        )

        self.assertEqual(report.placement_quality, "GOOD")
        self.assertEqual(report.fastener_coverage, "GOOD")

    def test_medium_risk_placement_quality_and_coverage(self):
        report = self.builder.build(
            self._minifix_report(is_valid=True, requires_review=True),
            self._confirmat_report(is_valid=True),
            self._hinge_report(),
        )

        self.assertEqual(report.placement_quality, "REVIEW")
        self.assertEqual(report.fastener_coverage, "REVIEW")

    def test_high_risk_placement_quality_and_coverage(self):
        report = self.builder.build(
            self._minifix_report(is_valid=False),
            self._confirmat_report(is_valid=True),
            self._hinge_report(),
        )

        self.assertEqual(report.placement_quality, "POOR")
        self.assertEqual(report.fastener_coverage, "POOR")

    def test_builder_does_not_mutate_inputs(self):
        minifix = self._minifix_report(is_valid=True, requires_review=True, tags=["a"])
        confirmat = self._confirmat_report(is_valid=True, tags=["b"])
        hinge = self._hinge_report(tags=["c"])
        snapshots = [
            self._snapshot(minifix),
            self._snapshot(confirmat),
            self._snapshot(hinge),
        ]

        self.builder.build(minifix, confirmat, hinge)

        self.assertEqual(
            [self._snapshot(minifix), self._snapshot(confirmat), self._snapshot(hinge)],
            snapshots,
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _minifix_report(is_valid=True, requires_review=False, tags=None):
        from manufacturing.minifix_validation_report import MinifixValidationReport

        report = MinifixValidationReport(is_valid=is_valid)
        report.requires_review = requires_review
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _confirmat_report(is_valid=True, requires_review=False, tags=None):
        from manufacturing.confirmat_validation_report import (
            ConfirmatValidationReport,
        )

        report = ConfirmatValidationReport(is_valid=is_valid)
        report.requires_review = requires_review
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _hinge_report(is_valid=True, requires_review=False, tags=None):
        from manufacturing.door_engineering_report import DoorEngineeringReport

        report = DoorEngineeringReport()
        report.is_valid = is_valid
        report.requires_review = requires_review
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
