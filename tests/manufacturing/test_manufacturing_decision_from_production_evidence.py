import importlib
import inspect
import unittest


class TestManufacturingDecisionFromProductionEvidence(unittest.TestCase):
    def test_builder_consumes_package_production_evidence(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )

        package = self._package_with_complete_evidence()

        decision = ManufacturingDecisionBuilder().build(production_evidence=package)

        self.assertEqual(decision.status, "PASS")
        self.assertTrue(decision.ready_for_production)
        self.assertEqual(decision.legacy_readiness_status, "READY")

    def test_door_hinge_warning_produces_review_decision(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )
        from tests.manufacturing.test_door_hardware_evidence_in_production_package import (
            TestDoorHardwareEvidenceInProductionPackage,
        )

        package = ManufacturingProductionPackageBuilder().build(
            TestDoorHardwareEvidenceInProductionPackage._package_with_door_without_hinge_metadata()
        )

        decision = ManufacturingDecisionBuilder().build(
            production_evidence=package.production_evidence
        )

        self.assertEqual(decision.status, "WARNING")
        self.assertFalse(decision.ready_for_production)
        self.assertEqual(decision.legacy_readiness_status, "REVIEW")
        self.assertIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            decision.warning_reasons,
        )

    def test_complete_evidence_without_warnings_passes(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )

        decision = ManufacturingDecisionBuilder().build(
            production_evidence=self._package_with_complete_evidence().production_evidence
        )

        self.assertEqual(decision.status, "PASS")
        self.assertTrue(decision.ready_for_production)
        self.assertEqual(decision.warning_reasons, ())
        self.assertEqual(decision.legacy_readiness_status, "READY")

    def test_blocking_validation_input_still_fails(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )
        from tests.manufacturing.test_manufacturing_decision_builder import (
            TestManufacturingDecisionBuilder,
        )

        decision = ManufacturingDecisionBuilder().build(
            production_evidence=self._package_with_complete_evidence().production_evidence,
            manufacturing_validation_summary_report=(
                TestManufacturingDecisionBuilder._validation_summary(
                    blocking_issue_count=1,
                    blocking_messages=["Missing material assignment"],
                )
            ),
        )

        self.assertEqual(decision.status, "FAIL")
        self.assertFalse(decision.ready_for_production)
        self.assertEqual(decision.legacy_readiness_status, "BLOCKED")
        self.assertIn("Missing material assignment", decision.blocking_reasons)

    def test_missing_existing_evidence_creates_warning(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        decision = ManufacturingDecisionBuilder().build(
            production_evidence=ManufacturingProductionPackage().production_evidence
        )

        self.assertEqual(decision.status, "WARNING")
        self.assertIn("Missing cutlist evidence", decision.warning_reasons)
        self.assertIn("Missing machining evidence", decision.warning_reasons)
        self.assertIn("Missing edge evidence", decision.warning_reasons)
        self.assertIn("Missing hardware evidence", decision.warning_reasons)

    def test_builder_has_no_forbidden_dependencies_or_calls(self):
        module = importlib.import_module("manufacturing.manufacturing_decision_builder")
        source = inspect.getsource(module)

        for token in (
            "GeometryEngine",
            "SceneGraph",
            "cost_intelligence",
            "Commercial",
            "ManufacturingValidator",
            "ManufacturingReleaseValidator",
            "ManufacturingProductionPackageBuilder",
            "HardwareUsageBuilder",
            "HardwareBomBuilder",
            ".validate(",
            ".build(",
        ):
            self.assertNotIn(token, source)

    @staticmethod
    def _package_with_complete_evidence():
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        return ManufacturingProductionPackage(
            cutlist_report=TestManufacturingDecisionFromProductionEvidence._report(
                items=[{"identity": "door-01"}]
            ),
            machining_report=TestManufacturingDecisionFromProductionEvidence._report(
                items=[{"operation_type": "DRILL"}]
            ),
            edge_report=TestManufacturingDecisionFromProductionEvidence._report(
                items=[{"edge": "TOP"}]
            ),
            hardware_report=TestManufacturingDecisionFromProductionEvidence._report(
                bom_rows=[{"hardware_sku": "HINGE_BLUM_110_V1"}]
            ),
            warnings=[],
        )

    @staticmethod
    def _report(**fields):
        return type("Report", (), fields)()


if __name__ == "__main__":
    unittest.main()
