import inspect
import unittest
from dataclasses import fields, is_dataclass
from unittest.mock import patch


class TestFactoryReleasePackage(unittest.TestCase):
    def test_factory_release_package_is_dataclass(self):
        from manufacturing.factory_release_package import FactoryReleasePackage

        self.assertTrue(is_dataclass(FactoryReleasePackage))

    def test_factory_release_package_field_inventory_is_stable(self):
        from manufacturing.factory_release_package import FactoryReleasePackage

        self.assertEqual(
            [field.name for field in fields(FactoryReleasePackage)],
            [
                "manufacturing_decision",
                "cut_list",
                "hardware_bom",
                "cnc_package",
                "assembly_package",
                "warnings",
                "metadata",
            ],
        )

    def test_factory_release_package_safe_defaults(self):
        from manufacturing.factory_release_package import FactoryReleasePackage

        package = FactoryReleasePackage()

        self.assertIsNone(package.manufacturing_decision)
        self.assertIsNone(package.cut_list)
        self.assertIsNone(package.hardware_bom)
        self.assertIsNone(package.cnc_package)
        self.assertIsNone(package.assembly_package)
        self.assertEqual(package.warnings, [])
        self.assertEqual(package.metadata, {})

    def test_factory_release_package_reuses_existing_objects_by_reference(self):
        from manufacturing.factory_release_package import FactoryReleasePackage

        decision = object()
        cut_list = object()
        hardware_bom = object()
        cnc_package = object()
        assembly_package = object()
        warnings = ["warning"]
        metadata = {"release": "v1.0"}

        package = FactoryReleasePackage(
            manufacturing_decision=decision,
            cut_list=cut_list,
            hardware_bom=hardware_bom,
            cnc_package=cnc_package,
            assembly_package=assembly_package,
            warnings=warnings,
            metadata=metadata,
        )

        self.assertIs(package.manufacturing_decision, decision)
        self.assertIs(package.cut_list, cut_list)
        self.assertIs(package.hardware_bom, hardware_bom)
        self.assertIs(package.cnc_package, cnc_package)
        self.assertIs(package.assembly_package, assembly_package)
        self.assertIs(package.warnings, warnings)
        self.assertIs(package.metadata, metadata)

    def test_empty_application_pipeline_builds_factory_release_package(self):
        from application.manufacturing_application_service import (
            ManufacturingApplicationService,
        )
        from domain.base_cabinet_manufacturing_outputs_entry import (
            BaseCabinetManufacturingOutputsEntryResult,
        )
        from domain.base_cabinet_specification import BaseCabinetSpecification
        from manufacturing.factory_release_package import FactoryReleasePackage

        entry_result = BaseCabinetManufacturingOutputsEntryResult(
            cut_list=object(),
            manufacturing_package=object(),
            metadata={},
        )

        with patch(
            "application.manufacturing_application_service."
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=entry_result,
        ), patch(
            "application.manufacturing_application_service."
            "ManufacturingProductionPackageBuilder",
        ) as package_builder_class, patch(
            "application.manufacturing_application_service."
            "ManufacturingDecisionBuilder",
        ) as decision_builder_class:
            production_package = type(
                "ProductionPackage",
                (),
                {
                    "hardware_report": object(),
                    "cnc_report": object(),
                    "assembly_report": object(),
                    "warnings": ["release-warning"],
                    "production_evidence": object(),
                },
            )()
            decision = object()
            package_builder_class.return_value.build.return_value = production_package
            decision_builder_class.return_value.build.return_value = decision

            result = ManufacturingApplicationService().execute(
                specification=BaseCabinetSpecification()
            )

        self.assertIn("factory_release_package", result.data)
        release_package = result.data["factory_release_package"]
        self.assertIsInstance(release_package, FactoryReleasePackage)
        self.assertIs(release_package.manufacturing_decision, decision)
        self.assertIs(release_package.cut_list, entry_result.cut_list)
        self.assertIs(release_package.hardware_bom, production_package.hardware_report)
        self.assertIs(release_package.cnc_package, production_package.cnc_report)
        self.assertIs(release_package.assembly_package, production_package.assembly_report)
        self.assertIs(release_package.warnings, production_package.warnings)
        self.assertIs(release_package.metadata, entry_result.metadata)

    def test_factory_release_package_has_no_business_logic(self):
        import manufacturing.factory_release_package as module

        source = inspect.getsource(module)

        for token in (
            "Builder",
            "Engine",
            "Workflow",
            "calculate",
            "validate",
            "optimiz",
            "geometry",
            "SceneGraph",
            "Commercial",
            "Cost",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
