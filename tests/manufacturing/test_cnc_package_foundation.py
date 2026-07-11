import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestCncPackageFoundation(unittest.TestCase):
    def test_cnc_report_contract_exists_and_is_dataclass(self):
        from manufacturing.cnc_report import CNCReport, CNCReportRow

        self.assertTrue(is_dataclass(CNCReport))
        self.assertTrue(is_dataclass(CNCReportRow))

    def test_cnc_report_row_field_inventory_is_stable(self):
        from manufacturing.cnc_report import CNCReportRow

        self.assertEqual(
            [field.name for field in fields(CNCReportRow)],
            [
                "panel_identity",
                "operation_type",
                "face",
                "x",
                "y",
                "z",
                "diameter",
                "depth",
                "axis",
                "is_through",
                "source_operation_reference",
            ],
        )

    def test_cnc_report_row_safe_defaults(self):
        from manufacturing.cnc_report import CNCReportRow

        row = CNCReportRow()

        self.assertEqual(row.panel_identity, "")
        self.assertEqual(row.operation_type, "")
        self.assertEqual(row.face, "")
        self.assertEqual(row.x, 0.0)
        self.assertEqual(row.y, 0.0)
        self.assertEqual(row.z, 0.0)
        self.assertEqual(row.diameter, 0.0)
        self.assertEqual(row.depth, 0.0)
        self.assertEqual(row.axis, "Z")
        self.assertFalse(row.is_through)
        self.assertEqual(row.source_operation_reference, "")

    def test_production_package_builder_exposes_cnc_report_from_machining(self):
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
                    is_through=False,
                    x=10.0,
                    y=20.0,
                    z=30.0,
                    face="BACK",
                    axis="Z",
                    source="door-01",
                ),
                UnifiedManufacturingOperation(
                    operation_type="DRILL",
                    diameter=3.0,
                    depth=12.0,
                    is_through=True,
                    x=40.0,
                    y=50.0,
                    z=60.0,
                    face="LEFT",
                    axis="X",
                    source="drawer-01",
                ),
            ]
        )

        production_package = ManufacturingProductionPackageBuilder().build(package)

        self.assertIsNotNone(production_package.cnc_report)
        self.assertEqual(len(production_package.cnc_report.rows), 2)
        first_row = production_package.cnc_report.rows[0]
        self.assertEqual(first_row.panel_identity, "door-01")
        self.assertEqual(first_row.operation_type, "DRILL")
        self.assertEqual(first_row.face, "BACK")
        self.assertEqual(first_row.diameter, 35.0)
        self.assertEqual(first_row.depth, 12.5)
        self.assertEqual(first_row.axis, "Z")
        self.assertEqual(first_row.source_operation_reference, "door-01")
        second_row = production_package.cnc_report.rows[1]
        self.assertEqual(second_row.panel_identity, "drawer-01")
        self.assertTrue(second_row.is_through)
        self.assertEqual(second_row.axis, "X")

    def test_empty_machining_operations_produce_empty_cnc_report(self):
        from manufacturing.manufacturing_package import ManufacturingPackage
        from manufacturing.manufacturing_production_package_builder import (
            ManufacturingProductionPackageBuilder,
        )

        production_package = ManufacturingProductionPackageBuilder().build(
            ManufacturingPackage()
        )

        self.assertIsNotNone(production_package.cnc_report)
        self.assertEqual(production_package.cnc_report.rows, [])
        self.assertEqual(production_package.cnc_report.warnings, [])

    def test_production_package_builder_prefers_preserved_panel_identity_over_source_fallback(self):
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
                    diameter=5.0,
                    depth=12.0,
                    face="LEFT",
                    axis="Z",
                    source="FaceDrill",
                    metadata={
                        "panel_identity": "SIDE-LEFT-01",
                        "source_operation_reference": "FaceDrill",
                    },
                )
            ]
        )

        production_package = ManufacturingProductionPackageBuilder().build(package)

        self.assertEqual(len(production_package.cnc_report.rows), 1)
        self.assertEqual(
            production_package.cnc_report.rows[0].panel_identity,
            "SIDE-LEFT-01",
        )
        self.assertEqual(
            production_package.cnc_report.rows[0].source_operation_reference,
            "FaceDrill",
        )

    def test_cnc_builder_uses_machining_report_only(self):
        import manufacturing.cnc_report_builder as module

        source = inspect.getsource(module)

        self.assertIn("machining_report", source)
        for token in (
            "GeometryEngine",
            "SceneGraph",
            "Commercial",
            "cost",
            "GCode",
            "postprocessor",
            "post-processor",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
