import unittest
from unittest.mock import patch

from services.manufacturing_dashboard_service import (
    ManufacturingDashboardService,
)

from scene_graph.scene_graph import SceneGraph


class TestDashboardServiceConsumesSceneGraph(
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
    def test_scene_graph_flows_to_extractor(
        self,
        extractor_cls,
        builder_cls,
        viewmodel_cls,
    ):
        report = object()

        extractor_cls.extract.return_value = [
            "panel_a",
            "panel_b",
        ]

        builder_cls.return_value.build.return_value = (
            report
        )

        scene_graph = SceneGraph()

        ManufacturingDashboardService.build(
            scene_graph
        )

        extractor_cls.extract.assert_called_once_with(
            scene_graph
        )


if __name__ == "__main__":
    unittest.main()
