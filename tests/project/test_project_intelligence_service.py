import unittest
from unittest.mock import patch

from services.project_intelligence_service import (
    ProjectIntelligenceService,
)


class TestProjectIntelligenceService(
    unittest.TestCase
):

    @patch(
        "services.project_intelligence_service.UnifiedDashboardService"
    )
    @patch(
        "services.project_intelligence_service.UnifiedIntelligenceReportBuilder"
    )
    @patch(
        "services.project_intelligence_service.HybridManufacturingExtractor"
    )
    def test_builds_unified_dashboard(
        self,
        extractor_cls,
        report_builder_cls,
        dashboard_service_cls,
    ):

        extractor_cls.extract.return_value = [
            "panel"
        ]

        report = object()

        report_builder_cls.return_value.build.return_value = (
            report
        )

        dashboard_result = object()

        dashboard_service_cls.return_value.build_from_report.return_value = (
            dashboard_result
        )

        result = (
            ProjectIntelligenceService.build(
                "scene_graph"
            )
        )

        self.assertIs(
            result,
            dashboard_result
        )

        extractor_cls.extract.assert_called_once_with(
            "scene_graph"
        )

        report_builder_cls.return_value.build.assert_called_once_with(
            ["panel"],
            scene_graph="scene_graph",
        )

        dashboard_service_cls.return_value.build_from_report.assert_called_once_with(
            report
        )


if __name__ == "__main__":
    unittest.main()
