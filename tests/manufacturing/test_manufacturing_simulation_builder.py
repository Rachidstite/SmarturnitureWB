import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestManufacturingSimulationBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_simulation_builder import (
            ManufacturingSimulationBuilder,
        )

        self.builder = ManufacturingSimulationBuilder()

    def test_report_contract(self):
        from manufacturing.manufacturing_simulation_report import (
            ManufacturingSimulationReport,
        )

        self.assertTrue(is_dataclass(ManufacturingSimulationReport))
        self.assertEqual(
            [field.name for field in fields(ManufacturingSimulationReport)],
            [
                "panel_count",
                "machining_operation_count",
                "edge_operation_count",
                "drilling_operation_count",
                "assembly_operation_count",
                "estimated_cnc_minutes",
                "estimated_edge_banding_minutes",
                "estimated_assembly_minutes",
                "estimated_total_factory_minutes",
                "simulation_status",
                "simulation_recommendation",
            ],
        )

        report = ManufacturingSimulationReport()
        self.assertEqual(report.panel_count, 0)
        self.assertEqual(report.machining_operation_count, 0)
        self.assertEqual(report.edge_operation_count, 0)
        self.assertEqual(report.drilling_operation_count, 0)
        self.assertEqual(report.assembly_operation_count, 0)
        self.assertEqual(report.estimated_cnc_minutes, 0.0)
        self.assertEqual(report.estimated_edge_banding_minutes, 0.0)
        self.assertEqual(report.estimated_assembly_minutes, 0.0)
        self.assertEqual(report.estimated_total_factory_minutes, 0.0)
        self.assertEqual(report.simulation_status, "READY")
        self.assertEqual(report.simulation_recommendation, "")

    def test_counts_panels(self):
        report = self.builder.build(self._package(panels=[object(), object()]))
        self.assertEqual(report.panel_count, 2)
        self.assertEqual(report.assembly_operation_count, 2)

    def test_counts_machining_operations(self):
        package = self._package(machining_operations=[object(), object(), object()])
        report = self.builder.build(package)
        self.assertEqual(report.machining_operation_count, 3)

    def test_counts_edge_operations(self):
        package = self._package(edge_operations=[object(), object()])
        report = self.builder.build(package)
        self.assertEqual(report.edge_operation_count, 2)

    def test_counts_drilling_operations(self):
        package = self._package(
            machining_operations=[
                self._op(operation_type="DRILL"),
                self._op(type="drilling"),
                self._op(name="pre-drill"),
                self._op(name="cut"),
            ]
        )
        report = self.builder.build(package)
        self.assertEqual(report.drilling_operation_count, 3)

    def test_estimates_cnc_minutes(self):
        package = self._package(machining_operations=[object(), object()])
        report = self.builder.build(package)
        self.assertEqual(report.estimated_cnc_minutes, 3.0)

    def test_estimates_edge_banding_minutes(self):
        package = self._package(edge_operations=[object(), object(), object(), object()])
        report = self.builder.build(package)
        self.assertEqual(report.estimated_edge_banding_minutes, 3.0)

    def test_estimates_assembly_minutes(self):
        package = self._package(panels=[object(), object(), object()])
        report = self.builder.build(package)
        self.assertEqual(report.estimated_assembly_minutes, 9.0)

    def test_estimates_total_factory_minutes(self):
        package = self._package(
            panels=[object(), object()],
            machining_operations=[object(), object()],
            edge_operations=[object(), object(), object(), object()],
        )
        report = self.builder.build(package)
        self.assertEqual(report.estimated_total_factory_minutes, 12.0)

    def test_warnings_create_review_status(self):
        package = self._package(warnings=["Missing cut list"])
        report = self.builder.build(package)
        self.assertEqual(report.simulation_status, "REVIEW")
        self.assertEqual(
            report.simulation_recommendation,
            "Review manufacturing package before production",
        )

    def test_safe_defaults(self):
        report = self.builder.build(self._package())
        self.assertEqual(report.panel_count, 0)
        self.assertEqual(report.machining_operation_count, 0)
        self.assertEqual(report.edge_operation_count, 0)
        self.assertEqual(report.drilling_operation_count, 0)
        self.assertEqual(report.simulation_status, "READY")
        self.assertEqual(report.simulation_recommendation, "")

    def test_builder_does_not_mutate_manufacturing_package(self):
        package = self._package(
            panels=[object()],
            machining_operations=[self._op(operation_type="DRILL")],
            edge_operations=[object()],
            warnings=["Check material"],
        )
        snapshot = self._snapshot(package)

        self.builder.build(package)

        self.assertEqual(self._snapshot(package), snapshot)

    @staticmethod
    def _snapshot(package):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in package.__dict__.items()
        }

    @staticmethod
    def _package(
        panels=None,
        machining_operations=None,
        edge_operations=None,
        warnings=None,
    ):
        from manufacturing.manufacturing_package import ManufacturingPackage

        return ManufacturingPackage(
            panels=list(panels or []),
            machining_operations=list(machining_operations or []),
            edge_operations=list(edge_operations or []),
            warnings=list(warnings or []),
        )

    @staticmethod
    def _op(**kwargs):
        return SimpleNamespace(**kwargs)


if __name__ == "__main__":
    unittest.main()
