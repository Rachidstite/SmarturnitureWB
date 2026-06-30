import inspect
import unittest
from dataclasses import FrozenInstanceError, is_dataclass


class TestProductionEvidenceView(unittest.TestCase):
    def test_view_exposes_same_report_objects_as_package(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
            ProductionEvidenceView,
        )

        cutlist = self._report(items=[{"identity": "door-01"}])
        machining = self._report(items=[{"operation_type": "DRILL"}])
        edge = self._report(items=[{"edge": "TOP"}])
        hardware = self._report(bom_rows=[{"hardware_sku": "HINGE"}])
        package = ManufacturingProductionPackage(
            cutlist_report=cutlist,
            machining_report=machining,
            edge_report=edge,
            hardware_report=hardware,
        )

        evidence = package.production_evidence

        self.assertTrue(is_dataclass(evidence))
        self.assertIsInstance(evidence, ProductionEvidenceView)
        self.assertIs(evidence.cutlist_report, package.cutlist_report)
        self.assertIs(evidence.machining_report, package.machining_report)
        self.assertIs(evidence.edge_report, package.edge_report)
        self.assertIs(evidence.hardware_report, package.hardware_report)

    def test_view_exposes_same_evidence_flags_as_package(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage(
            cutlist_report=self._report(items=[{"identity": "door-01"}]),
            machining_report=self._report(items=[{"operation_type": "DRILL"}]),
            edge_report=self._report(items=[]),
            hardware_report=self._report(bom_rows=[{"hardware_sku": "HINGE"}]),
            warnings=["warning"],
        )

        evidence = package.production_evidence

        self.assertEqual(evidence.has_cutlist_evidence, package.has_cutlist_evidence)
        self.assertEqual(evidence.has_machining_evidence, package.has_machining_evidence)
        self.assertEqual(evidence.has_edge_evidence, package.has_edge_evidence)
        self.assertEqual(evidence.has_hardware_evidence, package.has_hardware_evidence)
        self.assertEqual(
            evidence.has_release_warning_evidence,
            package.has_release_warning_evidence,
        )

    def test_release_warnings_are_exposed_without_copying(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        warnings = ["Door panels present but hinge hardware evidence is missing."]
        package = ManufacturingProductionPackage(warnings=warnings)

        self.assertIs(package.production_evidence.release_warnings, package.release_warnings)
        self.assertIs(package.production_evidence.release_warnings, warnings)

    def test_view_is_read_only(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        evidence = ManufacturingProductionPackage().production_evidence

        with self.assertRaises(FrozenInstanceError):
            evidence.has_cutlist_evidence = True

    def test_view_does_not_import_or_call_builders_or_validators(self):
        import manufacturing.manufacturing_production_package as module

        source = inspect.getsource(module)

        for token in (
            "Builder",
            "Validator",
            "validate(",
            "build(",
            "manufacturing_release_validator",
            "hardware_bom_builder",
            "hardware_usage_builder",
        ):
            self.assertNotIn(token, source)

    @staticmethod
    def _report(**fields):
        return type("Report", (), fields)()


if __name__ == "__main__":
    unittest.main()
