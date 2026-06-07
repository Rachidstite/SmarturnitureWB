import unittest
from unittest.mock import patch

from services.manufacturing_dashboard_service import (
    ManufacturingDashboardService,
)


class TestDashboardServiceReturnsResult(
    unittest.TestCase
):

    @patch(
        "services.manufacturing_dashboard_service.ManufacturingDashboardViewModel"
    )
    @patch(
        "services.manufacturing_dashboard_service.ManufacturingIntelligenceReportBuilder"
    )
    @patch(
        "services.manufacturing_dashboard_service.HybridManufacturingExtractor"
    )
    def test_returns_viewmodel_instance(
        self,
        extractor_cls,
        builder_cls,
        viewmodel_cls,
    ):
        report = object()

        expected_vm = object()

        extractor_cls.extract.return_value = [
            "panel"
        ]

        builder_cls.return_value.build.return_value = (
            report
        )

        viewmodel_cls.from_report.return_value = (
            expected_vm
        )

        result = (
            ManufacturingDashboardService.build(
                "scene_graph"
            )
        )

        self.assertIs(
            result,
            expected_vm,
        )


if __name__ == "__main__":
    unittest.main()
