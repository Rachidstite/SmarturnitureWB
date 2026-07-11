import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestAssemblyPackageFoundation(unittest.TestCase):
    def test_assembly_report_contract_exists_and_is_dataclass(self):
        from manufacturing.assembly_package_report import (
            AssemblyPanelInventoryRow,
            AssemblyPackageReport,
            AssemblyPackageRow,
        )

        self.assertTrue(is_dataclass(AssemblyPackageReport))
        self.assertTrue(is_dataclass(AssemblyPackageRow))
        self.assertTrue(is_dataclass(AssemblyPanelInventoryRow))

    def test_assembly_report_row_field_inventory_is_stable(self):
        from manufacturing.assembly_package_report import AssemblyPackageRow

        self.assertEqual(
            [field.name for field in fields(AssemblyPackageRow)],
            [
                "cabinet_reference",
                "component_reference",
                "assembly_group",
                "hardware_required",
                "hardware_quantity",
                "joinery_reference",
                "required_machining",
                "assembly_notes",
                "source_operation_references",
            ],
        )

    def test_assembly_report_row_safe_defaults(self):
        from manufacturing.assembly_package_report import AssemblyPackageRow

        row = AssemblyPackageRow()

        self.assertEqual(row.cabinet_reference, ())
        self.assertEqual(row.component_reference, ())
        self.assertEqual(row.assembly_group, "")
        self.assertEqual(row.hardware_required, "")
        self.assertEqual(row.hardware_quantity, 0)
        self.assertEqual(row.joinery_reference, ())
        self.assertEqual(row.required_machining, ())
        self.assertEqual(row.assembly_notes, ())
        self.assertEqual(row.source_operation_references, ())

    def test_assembly_panel_inventory_row_field_inventory_is_stable(self):
        from manufacturing.assembly_package_report import AssemblyPanelInventoryRow

        self.assertEqual(
            [field.name for field in fields(AssemblyPanelInventoryRow)],
            [
                "cabinet_reference",
                "component_reference",
                "panel_identity",
                "description",
                "quantity",
                "unit",
                "material",
                "width_mm",
                "height_mm",
                "thickness_mm",
                "component_role",
                "group",
            ],
        )

    def test_assembly_panel_inventory_row_is_immutable(self):
        from dataclasses import FrozenInstanceError

        from manufacturing.assembly_package_report import AssemblyPanelInventoryRow

        row = AssemblyPanelInventoryRow(
            cabinet_reference=(),
            component_reference=("side-left",),
            panel_identity="side-left",
            description="SIDE_PANEL",
            quantity=1,
            unit="pcs",
            material="MDF_18MM",
            width_mm=600.0,
            height_mm=720.0,
            thickness_mm=18.0,
            component_role="SIDE_PANEL",
            group="CARCASS",
        )

        with self.assertRaises(FrozenInstanceError):
            row.panel_identity = "other"

    def test_assembly_report_backward_compatible_default_construction_still_works(self):
        from manufacturing.assembly_package_report import AssemblyPackageReport

        report = AssemblyPackageReport()

        self.assertEqual(report.rows, [])
        self.assertEqual(report.panel_inventory, ())
        self.assertEqual(report.warnings, [])

    def test_empty_production_package_produces_empty_assembly_report(self):
        from manufacturing.assembly_package_builder import AssemblyPackageBuilder
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        report = AssemblyPackageBuilder().build(ManufacturingProductionPackage())

        self.assertEqual(report.rows, [])
        self.assertEqual(report.panel_inventory, ())
        self.assertEqual(report.warnings, [])

    def test_door_and_drawer_hardware_flow_into_assembly_report(self):
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        package = ManufacturingPackage(
            machining_operations=[
                UnifiedManufacturingOperation(
                    operation_type="DRILL",
                    diameter=35.0,
                    depth=12.5,
                    face="BACK",
                    axis="Z",
                    source="door-01::hinge-1",
                    metadata={
                        "hardware_family": "HINGE",
                        "hardware_sku": "HINGE_BLUM_110_V1",
                        "hardware_intent": "INTENT_HINGE",
                        "hardware_description": "Blum 110 degree hinge",
                        "hardware_category": "HINGE",
                        "hardware_unit": "pcs",
                        "component_reference": "door-01",
                        "cabinet_reference": "cabinet-01",
                        "source_operation_reference": "door-01::hinge-1",
                    },
                ),
                UnifiedManufacturingOperation(
                    operation_type="DRILL",
                    diameter=3.0,
                    depth=12.0,
                    face="LEFT",
                    axis="X",
                    source="drawer-01::slide-1",
                    metadata={
                        "hardware_family": "DRAWER_SLIDE",
                        "hardware_sku": "DRAWER_SLIDE_STANDARD_450",
                        "hardware_intent": "INTENT_DRAWER_SLIDE",
                        "hardware_description": "Drawer slide",
                        "hardware_category": "DRAWER_SLIDE",
                        "hardware_unit": "pcs",
                        "component_reference": "drawer-01",
                        "cabinet_reference": "cabinet-01",
                        "source_operation_reference": "drawer-01::slide-1",
                    },
                ),
            ]
        )

        production_package = ManufacturingProductionPackageBuilder().build(package)
        report = production_package.assembly_report

        self.assertIsNotNone(report)
        self.assertEqual(len(report.rows), 2)

        door_row = report.rows[0]
        self.assertEqual(door_row.cabinet_reference, ("cabinet-01",))
        self.assertEqual(door_row.component_reference, ("door-01",))
        self.assertEqual(door_row.assembly_group, "HINGE")
        self.assertEqual(door_row.hardware_required, "HINGE_BLUM_110_V1")
        self.assertEqual(door_row.hardware_quantity, 1)
        self.assertEqual(door_row.joinery_reference, ("door-01::hinge-1",))
        self.assertEqual(door_row.source_operation_references, ("door-01::hinge-1",))
        self.assertTrue(door_row.required_machining)
        self.assertEqual(door_row.required_machining[0].face, "BACK")

        drawer_row = report.rows[1]
        self.assertEqual(drawer_row.component_reference, ("drawer-01",))
        self.assertEqual(drawer_row.hardware_required, "DRAWER_SLIDE_STANDARD_450")
        self.assertEqual(drawer_row.joinery_reference, ("drawer-01::slide-1",))
        self.assertEqual(drawer_row.source_operation_references, ("drawer-01::slide-1",))

    def test_joinery_references_and_source_operations_propagate_when_available(self):
        from manufacturing.assembly_package_builder import AssemblyPackageBuilder
        from manufacturing.assembly_package_report import AssemblyPackageReport
        from manufacturing.hardware_bom_report import HardwareBomReport, HardwareBomRow
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage(
            hardware_report=HardwareBomReport(
                bom_rows=[
                    HardwareBomRow(
                        bom_category="HARDWARE",
                        sku="HINGE_BLUM_110_V1",
                        description="Blum 110 degree hinge",
                        quantity=2,
                        unit="pcs",
                        component_reference=("door-01",),
                        cabinet_reference=("cabinet-01",),
                        hardware_category="HINGE",
                        source_operation_references=(
                            "hinge-op-1",
                            "hinge-op-2",
                        ),
                    )
                ]
            ),
            cnc_report=type(
                "CncReport",
                (),
                {
                    "rows": [
                        type(
                            "CncRow",
                            (),
                            {
                                "source_operation_reference": "hinge-op-1",
                                "operation_type": "DRILL",
                                "face": "BACK",
                                "x": 1.0,
                                "y": 2.0,
                                "z": 3.0,
                                "diameter": 35.0,
                                "depth": 12.5,
                                "axis": "Z",
                                "is_through": False,
                            },
                        )(),
                        type(
                            "CncRow",
                            (),
                            {
                                "source_operation_reference": "hinge-op-2",
                                "operation_type": "DRILL",
                                "face": "BACK",
                                "x": 4.0,
                                "y": 5.0,
                                "z": 6.0,
                                "diameter": 2.5,
                                "depth": 12.5,
                                "axis": "Z",
                                "is_through": True,
                            },
                        )(),
                    ],
                    "warnings": [],
                },
            )(),
        )

        report = AssemblyPackageBuilder().build(package)

        self.assertIsInstance(report, AssemblyPackageReport)
        self.assertEqual(report.rows[0].joinery_reference, ("hinge-op-1", "hinge-op-2"))
        self.assertEqual(
            {row.source_operation_reference for row in report.rows[0].required_machining},
            {"hinge-op-1", "hinge-op-2"},
        )

    def test_assembly_builder_uses_existing_evidence_only(self):
        import manufacturing.assembly_package_builder as module

        source = inspect.getsource(module)

        for token in (
            "AssemblyEngine",
            "AssemblyWorkflow",
            "AssemblyPlanner",
            "AssemblyOptimizer",
            "GeometryEngine",
            "SceneGraph",
            "Commercial",
            "cost",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
