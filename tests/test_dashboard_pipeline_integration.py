import unittest
from unittest.mock import patch

from services.manufacturing_dashboard_service import (
    ManufacturingDashboardService,
)

from presentation.manufacturing_dashboard_presenter import (
    ManufacturingDashboardPresenter,
)

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from scene_graph.scene_graph import SceneGraph


class TestDashboardPipelineIntegration(
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
    def test_service_output_reaches_presenter(
        self,
        extractor_cls,
        builder_cls,
        viewmodel_cls,
    ):
        report = object()

        extractor_cls.extract.return_value = [
            "panel"
        ]

        builder_cls.return_value.build.return_value = (
            report
        )

        vm = ManufacturingDashboardViewModel(
            score=95,
            grade="A+",
            warning_count=1,
            recommendation_count=2,
            cost_impact_count=3,
            can_export=True,
        )

        viewmodel_cls.from_report.return_value = (
            vm
        )

        scene_graph = SceneGraph()

        result = (
            ManufacturingDashboardService.build(
                scene_graph
            )
        )

        presenter = (
            ManufacturingDashboardPresenter()
        )

        state = presenter.present(
            result.viewmodel
        )

        self.assertEqual(
            95,
            state.score,
        )

        self.assertEqual(
            "A+",
            state.grade,
        )

        self.assertTrue(
            state.can_export
        )


if __name__ == "__main__":
    unittest.main()
