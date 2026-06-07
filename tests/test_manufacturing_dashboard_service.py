import unittest
from unittest.mock import patch

from services.manufacturing_dashboard_service import (
    ManufacturingDashboardService,
)


class TestManufacturingDashboardService(
    unittest.TestCase
):

    @patch(
        "services.manufacturing_dashboard_service.ManufacturingDashboardViewModel"
    )
    @patch(
        "services.manufacturing_dashboard_service.HybridManufacturingExtractor"
    )
    @patch(
        "services.manufacturing_dashboard_service.ManufacturingIntelligenceReportBuilder"
    )
    def test_generates_dashboard_viewmodel(
        self,
        builder_cls,
        extractor_cls,
        viewmodel_cls,
    ):
        report = object()

        extractor_cls.extract.return_value = [
            "panel"
        ]

        builder_cls.return_value.build.return_value = (
            report
        )

        ManufacturingDashboardService.build(
            "scene_graph"
        )

        extractor_cls.extract.assert_called_once()

        builder_cls.return_value.build.assert_called_once()

        viewmodel_cls.from_report.assert_called_once_with(
            report
        )


if __name__ == "__main__":
    unittest.main()
