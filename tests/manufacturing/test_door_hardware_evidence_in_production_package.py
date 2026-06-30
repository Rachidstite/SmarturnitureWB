import inspect
import unittest


class TestDoorHardwareEvidenceInProductionPackage(unittest.TestCase):
    def test_door_package_exposes_hinge_hardware_evidence_when_available(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )

        production_package = ManufacturingProductionPackageBuilder().build(
            self._package_with_door_and_hinge_metadata()
        )

        self.assertIsNotNone(production_package.hardware_report)
        self.assertEqual(
            [
                (row.hardware_sku, row.quantity)
                for row in production_package.hardware_report.bom_rows
            ],
            [("HINGE_BLUM_110_V1", 2)],
        )
        self.assertNotIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            production_package.release_warnings,
        )

    def test_door_package_without_hinge_evidence_gets_release_warning(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )

        production_package = ManufacturingProductionPackageBuilder().build(
            self._package_with_door_without_hinge_metadata()
        )

        self.assertIsNotNone(production_package.hardware_report)
        self.assertEqual(production_package.hardware_report.bom_rows, [])
        self.assertIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            production_package.release_warnings,
        )

    def test_no_door_package_behavior_remains_unchanged(self):
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )

        production_package = ManufacturingProductionPackageBuilder().build(
            self._package_without_doors()
        )

        self.assertIsNotNone(production_package.hardware_report)
        self.assertNotIn(
            ManufacturingProductionPackageBuilder.DOOR_HINGE_WARNING,
            production_package.release_warnings,
        )

    def test_no_new_engine_workflow_or_forbidden_dependencies(self):
        import manufacturing.manufacturing_production_package_builder as module

        source = inspect.getsource(module)

        for token in (
            "GeometryEngine",
            "SceneGraph",
            "cost_intelligence",
            "Commercial",
            "HardwareEngine",
            "DoorHardwareBuilder",
            "Workflow",
        ):
            self.assertNotIn(token, source)

    @staticmethod
    def _package_with_door_and_hinge_metadata():
        package = TestDoorHardwareEvidenceInProductionPackage._package_with_door_without_hinge_metadata()
        package.machining_operations = [
            TestDoorHardwareEvidenceInProductionPackage._operation(
                hardware_family="HINGE",
                hardware_sku="HINGE_BLUM_110_V1",
                hardware_intent="INTENT_HINGE",
            ),
            TestDoorHardwareEvidenceInProductionPackage._operation(
                hardware_family="HINGE",
                hardware_sku="HINGE_BLUM_110_V1",
                hardware_intent="INTENT_HINGE",
            ),
        ]
        return package

    @staticmethod
    def _package_with_door_without_hinge_metadata():
        from manufacturing.edge_spec import EdgeSpec
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.material_spec import MaterialSpec
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )
        from shared.roles import NodeRole

        return ManufacturingPackage(
            panels=[
                PanelSpec(
                    identity="door-01",
                    role=NodeRole.DOOR_PANEL,
                    width=600.0,
                    height=720.0,
                    thickness=18.0,
                    material="MDF_18MM",
                    edge_spec=EdgeSpec(top="ABS_1MM"),
                )
            ],
            materials=[MaterialSpec(name="MDF_18MM", thickness=18.0)],
            machining_operations=[
                UnifiedManufacturingOperation(operation_type="DRILL")
            ],
            edge_operations=[
                UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
            ],
        )

    @staticmethod
    def _package_without_doors():
        from manufacturing.edge_spec import EdgeSpec
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.material_spec import MaterialSpec
        from manufacturing.panel_spec import PanelSpec
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )
        from shared.roles import NodeRole

        return ManufacturingPackage(
            panels=[
                PanelSpec(
                    identity="shelf-01",
                    role=NodeRole.SHELF,
                    width=600.0,
                    height=500.0,
                    thickness=18.0,
                    material="MDF_18MM",
                    edge_spec=EdgeSpec(top="ABS_1MM"),
                )
            ],
            materials=[MaterialSpec(name="MDF_18MM", thickness=18.0)],
            machining_operations=[
                UnifiedManufacturingOperation(operation_type="DRILL")
            ],
            edge_operations=[
                UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
            ],
        )

    @staticmethod
    def _operation(hardware_family, hardware_sku, hardware_intent):
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        return UnifiedManufacturingOperation(
            operation_type="DRILL",
            metadata={
                "hardware_family": hardware_family,
                "hardware_sku": hardware_sku,
                "hardware_intent": hardware_intent,
            },
        )


if __name__ == "__main__":
    unittest.main()
