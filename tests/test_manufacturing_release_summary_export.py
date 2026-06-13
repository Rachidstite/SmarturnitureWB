import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class TestManufacturingReleaseSummaryExport(unittest.TestCase):

    @patch(
        "exports.manufacturing_release_summary_export."
        "ManufacturingProjectIntelligencePipelineBuilder"
    )
    def test_generate_calls_project_pipeline_and_returns_result(
        self,
        pipeline_builder_class,
    ):
        from exports.manufacturing_release_summary_export import (
            ManufacturingReleaseSummaryExport,
        )

        scene_graph = object()
        project_result = object()
        pipeline_builder_class.return_value.build.return_value = project_result

        result = ManufacturingReleaseSummaryExport.generate(
            scene_graph,
            markup_rate=0.25,
            currency="EUR",
        )

        pipeline_builder_class.return_value.build.assert_called_once_with(
            scene_graph,
            0.25,
            "EUR",
        )
        self.assertIs(result, project_result)

    def test_export_csv_writes_production_package_summary(self):
        rows, raw_bytes = self._export_rows(self._project_result())

        self.assertTrue(raw_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(rows[0], ["section", "field", "value"])
        self.assertIn(["production_package", "release_ready", "True"], rows)
        self.assertIn(["production_package", "warning_count", "1"], rows)

    def test_export_csv_writes_output_report_type_names(self):
        rows, _raw_bytes = self._export_rows(self._project_result())

        self.assertIn(
            ["manufacturing_outputs", "cutlist_report", "CutlistReport"],
            rows,
        )
        self.assertIn(
            ["manufacturing_outputs", "edge_report", "EdgeReport"],
            rows,
        )
        self.assertIn(
            ["manufacturing_outputs", "machining_report", "MachiningReport"],
            rows,
        )
        self.assertIn(
            ["manufacturing_outputs", "summary_report", ""],
            rows,
        )

    def test_export_csv_writes_factory_intelligence_metrics(self):
        rows, _raw_bytes = self._export_rows(self._project_result())

        expected_rows = [
            ["factory_intelligence", "production_status", "READY"],
            ["factory_intelligence", "overall_score", "85"],
            ["factory_intelligence", "overall_grade", "A"],
            ["factory_intelligence", "total_manufacturing_cost", "1250.0"],
            ["factory_intelligence", "gross_margin_rate", "0.2"],
            ["factory_intelligence", "utilization_rate", "0.75"],
            ["factory_intelligence", "waste_rate", "0.25"],
            ["factory_intelligence", "recovery_score", "60"],
        ]
        for expected_row in expected_rows:
            self.assertIn(expected_row, rows)

    def test_export_csv_includes_warnings_and_recommendations(self):
        rows, _raw_bytes = self._export_rows(self._project_result())

        self.assertIn(["warnings", "warning", "Package warning"], rows)
        self.assertIn(["warnings", "warning", "Executive warning"], rows)
        self.assertIn(
            ["recommendations", "recommendation", "Review nesting"],
            rows,
        )

    @patch(
        "exports.manufacturing_release_summary_export."
        "ManufacturingProjectIntelligencePipelineBuilder"
    )
    def test_generate_does_not_mutate_scene_graph(self, pipeline_builder_class):
        from exports.manufacturing_release_summary_export import (
            ManufacturingReleaseSummaryExport,
        )
        from scene_graph.scene_graph import SceneGraph

        scene_graph = SceneGraph()
        original_nodes = scene_graph.nodes
        original_identity_map = scene_graph._identity_map
        pipeline_builder_class.return_value.build.return_value = object()

        ManufacturingReleaseSummaryExport.generate(scene_graph)

        self.assertIs(scene_graph.nodes, original_nodes)
        self.assertIs(scene_graph._identity_map, original_identity_map)
        self.assertEqual(scene_graph.nodes, [])
        self.assertEqual(scene_graph._identity_map, {})

    @staticmethod
    def _project_result():
        from cost_intelligence.manufacturing_executive_report import (
            ManufacturingExecutiveReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        class CutlistReport:
            pass

        class EdgeReport:
            pass

        class MachiningReport:
            pass

        production_package = ManufacturingProductionPackage(
            cutlist_report=CutlistReport(),
            edge_report=EdgeReport(),
            machining_report=MachiningReport(),
            summary_report=None,
            release_ready=True,
            warnings=["Package warning"],
        )
        executive_report = ManufacturingExecutiveReport(
            overall_score=85,
            overall_grade="A",
            production_status="READY",
            total_manufacturing_cost=1250.0,
            gross_margin_rate=0.20,
            utilization_rate=0.75,
            waste_rate=0.25,
            recovery_score=60,
            warnings=["Executive warning"],
            recommendations=["Review nesting"],
        )
        return SimpleNamespace(
            manufacturing_runtime_result=SimpleNamespace(
                manufacturing_production_package=production_package
            ),
            manufacturing_factory_intelligence_result=SimpleNamespace(
                manufacturing_executive_report=executive_report
            ),
        )

    @staticmethod
    def _export_rows(project_result):
        from exports.manufacturing_release_summary_export import (
            ManufacturingReleaseSummaryExport,
        )

        with tempfile.TemporaryDirectory() as directory:
            filepath = Path(directory) / "release_summary.csv"
            ManufacturingReleaseSummaryExport.export_csv(project_result, filepath)
            raw_bytes = filepath.read_bytes()
            with filepath.open(
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:
                rows = list(csv.reader(csv_file))
        return rows, raw_bytes


if __name__ == "__main__":
    unittest.main()
