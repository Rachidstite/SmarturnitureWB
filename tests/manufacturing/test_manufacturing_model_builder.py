import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestManufacturingModelBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_model_builder import (
            ManufacturingModelBuilder,
        )

        self.builder = ManufacturingModelBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_returns_manufacturing_model_report(self):
        from manufacturing.manufacturing_model_report import (
            ManufacturingModelReport,
        )

        report = self.builder.build(
            manufacturing_package=self._package(),
            manufacturing_summary_report=self._summary_report(),
        )

        self.assertIsInstance(report, ManufacturingModelReport)

    def test_maps_panel_count_from_summary(self):
        report = self.builder.build(
            manufacturing_package=self._package(panels=[object()]),
            manufacturing_summary_report=self._summary_report(total_panels=7),
        )
        self.assertEqual(report.panel_count, 7)

    def test_falls_back_panel_count_to_manufacturing_package(self):
        report = self.builder.build(
            manufacturing_package=self._package(panels=[object(), object(), object()]),
        )
        self.assertEqual(report.panel_count, 3)

    def test_leaves_component_counts_at_defaults(self):
        report = self.builder.build(
            manufacturing_package=self._package(),
            manufacturing_summary_report=self._summary_report(),
        )
        self.assertEqual(report.cabinet_count, 0)
        self.assertEqual(report.drawer_count, 0)
        self.assertEqual(report.door_count, 0)
        self.assertEqual(report.shelf_count, 0)
        self.assertEqual(report.back_panel_count, 0)

    def test_maps_inventory_counts_when_provided(self):
        from manufacturing.manufacturing_model_inventory_counts import (
            ManufacturingModelInventoryCounts,
        )

        counts = ManufacturingModelInventoryCounts(
            cabinet_count=4,
            door_count=8,
            shelf_count=12,
            back_panel_count=4,
        )

        report = self.builder.build(
            manufacturing_package=self._package(),
            manufacturing_summary_report=self._summary_report(),
            inventory_counts=counts,
        )

        self.assertEqual(report.cabinet_count, 4)
        self.assertEqual(report.door_count, 8)
        self.assertEqual(report.shelf_count, 12)
        self.assertEqual(report.back_panel_count, 4)
        self.assertEqual(report.drawer_count, 0)

    def test_inventory_counts_are_not_mutated(self):
        from manufacturing.manufacturing_model_inventory_counts import (
            ManufacturingModelInventoryCounts,
        )

        counts = ManufacturingModelInventoryCounts(
            cabinet_count=2,
            door_count=3,
            shelf_count=4,
            back_panel_count=5,
        )
        snapshot = counts.__dict__.copy()

        self.builder.build(inventory_counts=counts)

        self.assertEqual(counts.__dict__, snapshot)

    def test_maps_machining_operations(self):
        report = self.builder.build(
            manufacturing_summary_report=self._summary_report(
                total_machining_operations=9
            ),
        )
        self.assertEqual(report.total_machining_operations, 9)

    def test_maps_drilling_operations(self):
        report = self.builder.build(
            manufacturing_metrics_report=self._metrics_report(
                total_drilling_operations=11
            ),
        )
        self.assertEqual(report.total_drilling_operations, 11)

    def test_maps_edge_operations(self):
        report = self.builder.build(
            manufacturing_summary_report=self._summary_report(
                total_edge_operations=5
            ),
        )
        self.assertEqual(report.total_edge_operations, 5)

    def test_maps_assembly_operations(self):
        report = self.builder.build(
            manufacturing_package=self._package(panels=[object(), object()]),
            manufacturing_simulation_report=self._simulation_report(
                assembly_operation_count=8
            ),
        )
        self.assertEqual(report.total_assembly_operations, 8)

    def test_maps_hardware_counts_as_copies(self):
        usage = self._hardware_usage_report(
            hardware_sku_counts={"SKU1": 2},
            hardware_family_counts={"FAMILY": 3},
            hardware_intent_counts={"INTENT_HINGE": 4},
        )
        report = self.builder.build(hardware_usage_report=usage)

        self.assertEqual(report.hardware_sku_counts, {"SKU1": 2})
        self.assertEqual(report.hardware_family_counts, {"FAMILY": 3})
        self.assertEqual(report.hardware_intent_counts, {"INTENT_HINGE": 4})
        self.assertIsNot(report.hardware_sku_counts, usage.hardware_sku_counts)
        self.assertIsNot(report.hardware_family_counts, usage.hardware_family_counts)
        self.assertIsNot(report.hardware_intent_counts, usage.hardware_intent_counts)

    def test_maps_bom_rows_as_copy(self):
        bom = self._hardware_bom_report(bom_rows=[{"hardware_sku": "SKU1"}])
        report = self.builder.build(hardware_bom_report=bom)

        self.assertEqual(report.bom_rows, [{"hardware_sku": "SKU1"}])
        self.assertIsNot(report.bom_rows, bom.bom_rows)

    def test_maps_metrics_fields(self):
        report = self.builder.build(
            manufacturing_metrics_report=self._metrics_report(
                total_panel_area_m2=12.5,
                total_edge_meters=9.75,
                machining_operations_by_type={"DRILL": 4},
            )
        )
        self.assertEqual(report.total_panel_area_m2, 12.5)
        self.assertEqual(report.total_edge_meters, 9.75)
        self.assertEqual(report.sheet_utilization_percent, 0.0)
        self.assertEqual(report.machining_operations_by_type, {"DRILL": 4})

    def test_maps_duration_fields(self):
        report = self.builder.build(
            manufacturing_duration_report=self._duration_report(
                estimated_cnc_minutes=10.0,
                estimated_drilling_minutes=2.0,
                estimated_edge_banding_minutes=3.0,
                estimated_assembly_minutes=4.0,
                total_production_minutes=19.0,
            )
        )
        self.assertEqual(report.estimated_cnc_minutes, 10.0)
        self.assertEqual(report.estimated_drilling_minutes, 2.0)
        self.assertEqual(report.estimated_edge_banding_minutes, 3.0)
        self.assertEqual(report.estimated_assembly_minutes, 4.0)
        self.assertEqual(report.total_production_minutes, 19.0)

    def test_falls_back_duration_fields_to_simulation(self):
        report = self.builder.build(
            manufacturing_simulation_report=self._simulation_report(
                estimated_cnc_minutes=12.0,
                estimated_drilling_minutes=5.0,
                estimated_edge_banding_minutes=6.0,
                estimated_assembly_minutes=7.0,
                estimated_total_factory_minutes=30.0,
            )
        )
        self.assertEqual(report.estimated_cnc_minutes, 12.0)
        self.assertEqual(report.estimated_drilling_minutes, 5.0)
        self.assertEqual(report.estimated_edge_banding_minutes, 6.0)
        self.assertEqual(report.estimated_assembly_minutes, 7.0)
        self.assertEqual(report.total_production_minutes, 30.0)

    def test_combines_warnings_without_mutating_inputs(self):
        package = self._package(warnings=["Package warning"])
        summary = self._summary_report(warnings=["Summary warning"])
        metrics = self._metrics_report(warnings=["Metrics warning"])
        duration = self._duration_report(warnings=["Duration warning"])
        bom = self._hardware_bom_report(warnings=["BOM warning"])
        joinery = self._joinery_report(warnings=["Joinery warning"])
        simulation = self._simulation_report(warnings=["Simulation warning"])

        snapshots = [
            self._snapshot(package),
            self._snapshot(summary),
            self._snapshot(metrics),
            self._snapshot(duration),
            self._snapshot(bom),
            self._snapshot(joinery),
            self._snapshot(simulation),
        ]

        report = self.builder.build(
            manufacturing_package=package,
            manufacturing_summary_report=summary,
            manufacturing_metrics_report=metrics,
            manufacturing_duration_report=duration,
            hardware_bom_report=bom,
            joinery_intelligence_report=joinery,
            manufacturing_simulation_report=simulation,
        )

        self.assertEqual(
            report.warnings,
            [
                "Package warning",
                "Summary warning",
                "Metrics warning",
                "Duration warning",
                "BOM warning",
                "Joinery warning",
                "Simulation warning",
            ],
        )
        self.assertEqual(
            [
                self._snapshot(package),
                self._snapshot(summary),
                self._snapshot(metrics),
                self._snapshot(duration),
                self._snapshot(bom),
                self._snapshot(joinery),
                self._snapshot(simulation),
            ],
            snapshots,
        )

    def test_sets_manufacturing_status_review_when_warnings_exist(self):
        report = self.builder.build(
            manufacturing_package=self._package(warnings=["Warning"]),
        )
        self.assertEqual(report.manufacturing_status, "REVIEW")

    def test_sets_manufacturing_status_ready_when_sources_exist_and_no_warnings(self):
        report = self.builder.build(
            manufacturing_package=self._package(),
            manufacturing_summary_report=self._summary_report(),
        )
        self.assertEqual(report.manufacturing_status, "READY")

    def test_sets_manufacturing_status_unknown_when_no_sources_exist(self):
        report = self.builder.build()
        self.assertEqual(report.manufacturing_status, "UNKNOWN")

    def test_no_embedded_report_objects_are_populated(self):
        report = self.builder.build(
            manufacturing_package=self._package(),
            manufacturing_summary_report=self._summary_report(),
            manufacturing_metrics_report=self._metrics_report(),
            manufacturing_duration_report=self._duration_report(),
            hardware_usage_report=self._hardware_usage_report(),
            hardware_bom_report=self._hardware_bom_report(),
            joinery_intelligence_report=self._joinery_report(),
            manufacturing_simulation_report=self._simulation_report(),
            project_name="Kitchen Project",
        )

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
        self.assertTrue(forbidden.isdisjoint(report.__dict__.keys()))

    def test_builder_does_not_mutate_any_input(self):
        package = self._package(
            panels=[object()],
            materials=[object()],
            machining_operations=[object()],
            edge_operations=[object()],
            warnings=["Package warning"],
        )
        summary = self._summary_report(
            total_panels=1,
            total_materials=1,
            total_edge_operations=1,
            total_machining_operations=1,
            warnings=["Summary warning"],
        )
        metrics = self._metrics_report(
            total_panel_area_m2=1.2,
            total_edge_meters=3.4,
            total_drilling_operations=5,
            machining_operations_by_type={"DRILL": 1},
            warnings=["Metrics warning"],
        )
        duration = self._duration_report(
            estimated_cnc_minutes=6.0,
            estimated_drilling_minutes=7.0,
            estimated_edge_banding_minutes=8.0,
            estimated_assembly_minutes=9.0,
            total_production_minutes=30.0,
            warnings=["Duration warning"],
        )
        usage = self._hardware_usage_report(
            hardware_sku_counts={"SKU1": 1},
            hardware_family_counts={"FAMILY": 2},
            hardware_intent_counts={"INTENT_HINGE": 3},
        )
        bom = self._hardware_bom_report(bom_rows=[{"hardware_sku": "SKU1"}], warnings=["BOM warning"])
        joinery = self._joinery_report(
            total_minifix=1,
            total_hinges=2,
            total_drawer_slides=3,
            total_handles=4,
            warnings=["Joinery warning"],
        )
        simulation = self._simulation_report(
            panel_count=1,
            machining_operation_count=1,
            edge_operation_count=1,
            drilling_operation_count=1,
            assembly_operation_count=1,
            estimated_cnc_minutes=1.0,
            estimated_drilling_minutes=1.0,
            estimated_edge_banding_minutes=1.0,
            estimated_assembly_minutes=1.0,
            estimated_total_factory_minutes=4.0,
            warnings=["Simulation warning"],
        )

        inputs = [
            package,
            summary,
            metrics,
            duration,
            usage,
            bom,
            joinery,
            simulation,
        ]
        snapshots = [self._snapshot(report) for report in inputs]

        self.builder.build(
            manufacturing_package=package,
            manufacturing_summary_report=summary,
            manufacturing_metrics_report=metrics,
            manufacturing_duration_report=duration,
            hardware_usage_report=usage,
            hardware_bom_report=bom,
            joinery_intelligence_report=joinery,
            manufacturing_simulation_report=simulation,
            project_name="Kitchen Project",
        )

        self.assertEqual([self._snapshot(report) for report in inputs], snapshots)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else dict(value) if isinstance(value, dict) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _package(panels=None, materials=None, machining_operations=None, edge_operations=None, warnings=None):
        from manufacturing.manufacturing_package import ManufacturingPackage

        return ManufacturingPackage(
            panels=list(panels or []),
            materials=list(materials or []),
            machining_operations=list(machining_operations or []),
            edge_operations=list(edge_operations or []),
            warnings=list(warnings or []),
        )

    @staticmethod
    def _summary_report(
        total_panels=0,
        total_materials=0,
        total_edge_operations=0,
        total_machining_operations=0,
        warnings=None,
    ):
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        return ManufacturingSummaryReport(
            total_panels=total_panels,
            total_materials=total_materials,
            total_edge_operations=total_edge_operations,
            total_machining_operations=total_machining_operations,
            warnings=list(warnings or []),
        )

    @staticmethod
    def _metrics_report(
        total_panel_area_m2=0.0,
        total_edge_meters=0.0,
        total_drilling_operations=0,
        machining_operations_by_type=None,
        warnings=None,
    ):
        from manufacturing.manufacturing_metrics_report import (
            ManufacturingMetricsReport,
        )

        return ManufacturingMetricsReport(
            total_panel_area_m2=total_panel_area_m2,
            total_edge_meters=total_edge_meters,
            total_drilling_operations=total_drilling_operations,
            machining_operations_by_type=dict(machining_operations_by_type or {}),
            warnings=list(warnings or []),
        )

    @staticmethod
    def _duration_report(
        estimated_cnc_minutes=0.0,
        estimated_drilling_minutes=0.0,
        estimated_edge_banding_minutes=0.0,
        estimated_assembly_minutes=0.0,
        total_production_minutes=0.0,
        warnings=None,
    ):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        return ManufacturingDurationReport(
            estimated_cnc_minutes=estimated_cnc_minutes,
            estimated_drilling_minutes=estimated_drilling_minutes,
            estimated_edge_banding_minutes=estimated_edge_banding_minutes,
            estimated_assembly_minutes=estimated_assembly_minutes,
            total_production_minutes=total_production_minutes,
            warnings=list(warnings or []),
        )

    @staticmethod
    def _hardware_usage_report(
        hardware_sku_counts=None,
        hardware_family_counts=None,
        hardware_intent_counts=None,
    ):
        from manufacturing.hardware_usage_report import HardwareUsageReport

        return HardwareUsageReport(
            hardware_sku_counts=dict(hardware_sku_counts or {}),
            hardware_family_counts=dict(hardware_family_counts or {}),
            hardware_intent_counts=dict(hardware_intent_counts or {}),
        )

    @staticmethod
    def _hardware_bom_report(bom_rows=None, warnings=None):
        from manufacturing.hardware_bom_report import HardwareBomReport

        return HardwareBomReport(
            bom_rows=list(bom_rows or []),
            warnings=list(warnings or []),
        )

    @staticmethod
    def _joinery_report(
        total_minifix=0,
        total_hinges=0,
        total_drawer_slides=0,
        total_handles=0,
        warnings=None,
    ):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        return JoineryIntelligenceReport(
            total_minifix=total_minifix,
            total_hinges=total_hinges,
            total_drawer_slides=total_drawer_slides,
            total_handles=total_handles,
            warnings=list(warnings or []),
        )

    @staticmethod
    def _simulation_report(
        panel_count=0,
        machining_operation_count=0,
        edge_operation_count=0,
        drilling_operation_count=0,
        assembly_operation_count=0,
        estimated_cnc_minutes=0.0,
        estimated_drilling_minutes=0.0,
        estimated_edge_banding_minutes=0.0,
        estimated_assembly_minutes=0.0,
        estimated_total_factory_minutes=0.0,
        simulation_status="READY",
        simulation_recommendation="",
        warnings=None,
    ):
        return SimpleNamespace(
            panel_count=panel_count,
            machining_operation_count=machining_operation_count,
            edge_operation_count=edge_operation_count,
            drilling_operation_count=drilling_operation_count,
            assembly_operation_count=assembly_operation_count,
            estimated_cnc_minutes=estimated_cnc_minutes,
            estimated_drilling_minutes=estimated_drilling_minutes,
            estimated_edge_banding_minutes=estimated_edge_banding_minutes,
            estimated_assembly_minutes=estimated_assembly_minutes,
            estimated_total_factory_minutes=estimated_total_factory_minutes,
            simulation_status=simulation_status,
            simulation_recommendation=simulation_recommendation,
            warnings=list(warnings or []),
        )


if __name__ == "__main__":
    unittest.main()
