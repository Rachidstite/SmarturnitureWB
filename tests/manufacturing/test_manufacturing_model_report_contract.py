import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingModelReportContract(unittest.TestCase):

    def test_manufacturing_model_report_is_dataclass(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        self.assertTrue(is_dataclass(ManufacturingModelReport))

    def test_field_order_is_exact(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingModelReport)],
            [
                "project_name",
                "cabinet_count",
                "panel_count",
                "drawer_count",
                "door_count",
                "shelf_count",
                "back_panel_count",
                "total_physical_parts",
                "total_sheet_count",
                "total_machining_operations",
                "total_drilling_operations",
                "total_edge_operations",
                "total_assembly_operations",
                "total_minifix",
                "total_confirmats",
                "total_hinges",
                "total_drawer_slides",
                "total_handles",
                "hardware_sku_counts",
                "hardware_family_counts",
                "hardware_intent_counts",
                "bom_rows",
                "total_panel_area_m2",
                "total_edge_meters",
                "sheet_utilization_percent",
                "machining_operations_by_type",
                "estimated_cnc_minutes",
                "estimated_drilling_minutes",
                "estimated_edge_banding_minutes",
                "estimated_assembly_minutes",
                "total_production_minutes",
                "manufacturing_status",
                "warnings",
                "blocking_issues",
                "recommendations",
            ],
        )

    def test_safe_defaults_match_contract(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        report = ManufacturingModelReport()

        self.assertEqual(report.project_name, "")
        self.assertEqual(report.cabinet_count, 0)
        self.assertEqual(report.panel_count, 0)
        self.assertEqual(report.drawer_count, 0)
        self.assertEqual(report.door_count, 0)
        self.assertEqual(report.shelf_count, 0)
        self.assertEqual(report.back_panel_count, 0)
        self.assertEqual(report.total_physical_parts, 0)
        self.assertEqual(report.total_sheet_count, 0)
        self.assertEqual(report.total_machining_operations, 0)
        self.assertEqual(report.total_drilling_operations, 0)
        self.assertEqual(report.total_edge_operations, 0)
        self.assertEqual(report.total_assembly_operations, 0)
        self.assertEqual(report.total_minifix, 0)
        self.assertEqual(report.total_confirmats, 0)
        self.assertEqual(report.total_hinges, 0)
        self.assertEqual(report.total_drawer_slides, 0)
        self.assertEqual(report.total_handles, 0)
        self.assertEqual(report.hardware_sku_counts, {})
        self.assertEqual(report.hardware_family_counts, {})
        self.assertEqual(report.hardware_intent_counts, {})
        self.assertEqual(report.bom_rows, [])
        self.assertEqual(report.total_panel_area_m2, 0.0)
        self.assertEqual(report.total_edge_meters, 0.0)
        self.assertEqual(report.sheet_utilization_percent, 0.0)
        self.assertEqual(report.machining_operations_by_type, {})
        self.assertEqual(report.estimated_cnc_minutes, 0.0)
        self.assertEqual(report.estimated_drilling_minutes, 0.0)
        self.assertEqual(report.estimated_edge_banding_minutes, 0.0)
        self.assertEqual(report.estimated_assembly_minutes, 0.0)
        self.assertEqual(report.total_production_minutes, 0.0)
        self.assertEqual(report.manufacturing_status, "UNKNOWN")
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.blocking_issues, [])
        self.assertEqual(report.recommendations, [])

    def test_dict_and_list_defaults_are_independent(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        first = ManufacturingModelReport()
        second = ManufacturingModelReport()

        self.assertIsNot(first.hardware_sku_counts, second.hardware_sku_counts)
        self.assertIsNot(first.hardware_family_counts, second.hardware_family_counts)
        self.assertIsNot(first.hardware_intent_counts, second.hardware_intent_counts)
        self.assertIsNot(first.bom_rows, second.bom_rows)
        self.assertIsNot(first.machining_operations_by_type, second.machining_operations_by_type)
        self.assertIsNot(first.warnings, second.warnings)
        self.assertIsNot(first.blocking_issues, second.blocking_issues)
        self.assertIsNot(first.recommendations, second.recommendations)

    def test_no_embedded_report_object_fields_exist(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        field_names = {field.name for field in fields(ManufacturingModelReport)}
        forbidden = {
            "manufacturing_package",
            "manufacturing_production_package",
            "summary_report",
            "duration_report",
            "metrics_report",
            "joinery_intelligence_report",
            "assembly_intelligence_report",
            "hardware_usage_report",
            "hardware_bom_report",
        }

        self.assertTrue(forbidden.isdisjoint(field_names))

    def test_manufacturing_model_report_has_no_methods_beyond_dataclass_defaults(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        method_names = {
            name
            for name, value in ManufacturingModelReport.__dict__.items()
            if callable(value) and not name.startswith("__")
        }

        self.assertEqual(method_names, set())

    def test_existing_manufacturing_package_contract_remains_unchanged(self):
        from manufacturing.manufacturing_package import ManufacturingPackage

        package = ManufacturingPackage()

        self.assertEqual(
            [field.name for field in fields(ManufacturingPackage)],
            [
                "panels",
                "materials",
                "machining_operations",
                "edge_operations",
                "warnings",
            ],
        )
        self.assertEqual(package.panels, [])
        self.assertEqual(package.materials, [])
        self.assertEqual(package.machining_operations, [])
        self.assertEqual(package.edge_operations, [])
        self.assertEqual(package.warnings, [])


if __name__ == "__main__":
    unittest.main()
