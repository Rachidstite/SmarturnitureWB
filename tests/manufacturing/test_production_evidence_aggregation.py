import inspect
import unittest


class TestProductionEvidenceAggregation(unittest.TestCase):
    def test_reports_cutlist_machining_and_edge_evidence_from_existing_reports(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage(
            cutlist_report=self._report(items=[{"identity": "door-01"}]),
            machining_report=self._report(items=[{"operation_type": "DRILL"}]),
            edge_report=self._report(items=[{"edge": "TOP"}]),
        )

        self.assertTrue(package.has_cutlist_evidence)
        self.assertTrue(package.has_machining_evidence)
        self.assertTrue(package.has_edge_evidence)

    def test_reports_hardware_evidence_from_existing_hardware_report(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage(
            hardware_report=self._report(bom_rows=[{"hardware_sku": "HINGE"}]),
        )

        self.assertTrue(package.has_hardware_evidence)

    def test_door_package_without_hinge_evidence_has_release_warning_evidence(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )
        from tests.manufacturing.test_door_hardware_evidence_in_production_package import (
            TestDoorHardwareEvidenceInProductionPackage,
        )

        package = ManufacturingProductionPackageBuilder().build(
            TestDoorHardwareEvidenceInProductionPackage._package_with_door_without_hinge_metadata()
        )

        self.assertTrue(package.has_cutlist_evidence)
        self.assertFalse(package.has_hardware_evidence)
        self.assertTrue(package.has_release_warning_evidence)

    def test_no_door_package_without_hardware_rows_does_not_claim_hardware_evidence(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )
        from tests.manufacturing.test_door_hardware_evidence_in_production_package import (
            TestDoorHardwareEvidenceInProductionPackage,
        )

        package = ManufacturingProductionPackageBuilder().build(
            TestDoorHardwareEvidenceInProductionPackage._package_without_doors()
        )

        self.assertTrue(package.has_cutlist_evidence)
        self.assertFalse(package.has_hardware_evidence)

    def test_evidence_properties_do_not_import_builders_or_validators(self):
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
