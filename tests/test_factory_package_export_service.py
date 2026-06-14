import copy
import tempfile
import unittest
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class TestFactoryPackageExportResult(unittest.TestCase):

    def test_result_is_dataclass_with_exact_field_order(self):
        from services.factory_package_export_result import (
            FactoryPackageExportResult,
        )

        self.assertTrue(is_dataclass(FactoryPackageExportResult))
        self.assertEqual(
            [field.name for field in fields(FactoryPackageExportResult)],
            [
                "project_intelligence_result",
                "executive_report_path",
                "release_summary_path",
            ],
        )


class TestFactoryPackageExportService(unittest.TestCase):

    @patch(
        "services.factory_package_export_service."
        "ManufacturingReleaseSummaryExport"
    )
    @patch(
        "services.factory_package_export_service."
        "ManufacturingExecutiveExport"
    )
    @patch(
        "services.factory_package_export_service."
        "ManufacturingProjectIntelligencePipelineBuilder"
    )
    def test_export_orchestrates_factory_package_exports(
        self,
        pipeline_builder_class,
        executive_export,
        release_summary_export,
    ):
        from services.factory_package_export_service import (
            FactoryPackageExportService,
        )

        scene_graph = {"nodes": [{"uid": "PANEL-1"}]}
        original_scene_graph = copy.deepcopy(scene_graph)
        executive_report = object()
        project_intelligence_result = SimpleNamespace(
            manufacturing_factory_intelligence_result=SimpleNamespace(
                manufacturing_executive_report=executive_report
            )
        )
        pipeline_builder_class.return_value.build.return_value = (
            project_intelligence_result
        )

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "factory-package"
            result = FactoryPackageExportService.export(
                scene_graph,
                output_dir,
                markup_rate=0.25,
                currency="EUR",
            )

            executive_report_path = output_dir / "Executive_Report.csv"
            release_summary_path = output_dir / "Release_Summary.csv"

            self.assertTrue(output_dir.is_dir())
            pipeline_builder_class.return_value.build.assert_called_once_with(
                scene_graph,
                0.25,
                "EUR",
            )
            executive_export.generate.assert_not_called()
            release_summary_export.generate.assert_not_called()
            executive_export.export_csv.assert_called_once_with(
                executive_report,
                executive_report_path,
            )
            release_summary_export.export_csv.assert_called_once_with(
                project_intelligence_result,
                release_summary_path,
            )
            self.assertIs(
                result.project_intelligence_result,
                project_intelligence_result,
            )
            self.assertEqual(result.executive_report_path, executive_report_path)
            self.assertEqual(result.release_summary_path, release_summary_path)
            self.assertEqual(scene_graph, original_scene_graph)


if __name__ == "__main__":
    unittest.main()
