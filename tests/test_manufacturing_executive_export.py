import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class TestManufacturingExecutiveExport(unittest.TestCase):

    @patch(
        "exports.manufacturing_executive_export."
        "ManufacturingProjectIntelligencePipelineBuilder"
    )
    def test_generate_calls_project_pipeline_and_returns_executive_report(
        self,
        pipeline_builder_class,
    ):
        from exports.manufacturing_executive_export import (
            ManufacturingExecutiveExport,
        )

        scene_graph = object()
        executive_report = object()
        pipeline_builder_class.return_value.build.return_value = SimpleNamespace(
            manufacturing_factory_intelligence_result=SimpleNamespace(
                manufacturing_executive_report=executive_report
            )
        )

        result = ManufacturingExecutiveExport.generate(
            scene_graph,
            markup_rate=0.25,
            currency="EUR",
        )

        pipeline_builder_class.return_value.build.assert_called_once_with(
            scene_graph,
            0.25,
            "EUR",
        )
        self.assertIs(result, executive_report)

    def test_export_csv_writes_expected_headers_and_values(self):
        from cost_intelligence.manufacturing_executive_report import (
            ManufacturingExecutiveReport,
        )
        from exports.manufacturing_executive_export import (
            ManufacturingExecutiveExport,
        )

        report = ManufacturingExecutiveReport(
            overall_score=85,
            overall_grade="A",
            production_status="READY",
            total_manufacturing_cost=1250.0,
            gross_margin_rate=0.20,
            utilization_rate=0.75,
            waste_rate=0.25,
            recovery_score=60,
        )

        rows, raw_bytes = self._export_rows(report)

        self.assertTrue(raw_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(rows[0], ["field", "value"])
        self.assertEqual(
            rows[1:],
            [
                ["overall_score", "85"],
                ["overall_grade", "A"],
                ["production_status", "READY"],
                ["total_manufacturing_cost", "1250.0"],
                ["gross_margin_rate", "0.2"],
                ["utilization_rate", "0.75"],
                ["waste_rate", "0.25"],
                ["recovery_score", "60"],
            ],
        )

    def test_export_csv_includes_warnings_and_recommendations(self):
        from cost_intelligence.manufacturing_executive_report import (
            ManufacturingExecutiveReport,
        )

        report = ManufacturingExecutiveReport(
            warnings=["First warning", "Second warning"],
            recommendations=["Review nesting"],
        )

        rows, _raw_bytes = self._export_rows(report)

        self.assertIn(["warning", "First warning"], rows)
        self.assertIn(["warning", "Second warning"], rows)
        self.assertIn(["recommendation", "Review nesting"], rows)

    @patch(
        "exports.manufacturing_executive_export."
        "ManufacturingProjectIntelligencePipelineBuilder"
    )
    def test_generate_does_not_mutate_scene_graph(self, pipeline_builder_class):
        from exports.manufacturing_executive_export import (
            ManufacturingExecutiveExport,
        )
        from scene_graph.scene_graph import SceneGraph

        scene_graph = SceneGraph()
        original_nodes = scene_graph.nodes
        original_identity_map = scene_graph._identity_map
        pipeline_builder_class.return_value.build.return_value = SimpleNamespace(
            manufacturing_factory_intelligence_result=SimpleNamespace(
                manufacturing_executive_report=object()
            )
        )

        ManufacturingExecutiveExport.generate(scene_graph)

        self.assertIs(scene_graph.nodes, original_nodes)
        self.assertIs(scene_graph._identity_map, original_identity_map)
        self.assertEqual(scene_graph.nodes, [])
        self.assertEqual(scene_graph._identity_map, {})

    @staticmethod
    def _export_rows(report):
        from exports.manufacturing_executive_export import (
            ManufacturingExecutiveExport,
        )

        with tempfile.TemporaryDirectory() as directory:
            filepath = Path(directory) / "executive.csv"
            ManufacturingExecutiveExport.export_csv(report, filepath)
            raw_bytes = filepath.read_bytes()
            with filepath.open(
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:
                rows = list(csv.reader(csv_file))
        return rows, raw_bytes


if __name__ == "__main__":
    unittest.main()
