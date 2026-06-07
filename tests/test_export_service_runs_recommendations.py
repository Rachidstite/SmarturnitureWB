import unittest
from unittest.mock import patch

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportServiceRecommendations(
    unittest.TestCase
):

    @patch(
        "services.canonical_manufacturing_export_service.CanonicalCSVExporter.export"
    )
    @patch(
        "services.canonical_manufacturing_export_service.CanonicalCNCExporter.export_rows"
    )
    @patch(
        "services.canonical_manufacturing_export_service.RecommendationEngine"
    )
    @patch(
        "services.canonical_manufacturing_export_service.ManufacturingRuleEngine"
    )
    @patch(
        "services.canonical_manufacturing_export_service.HybridManufacturingExtractor.extract"
    )
    def test_recommendations_are_executed(
        self,
        extract,
        engine_cls,
        recommendation_cls,
        exporter,
        csv_export
    ):

        extract.return_value = []

        engine = engine_cls.return_value
        engine.validate.return_value = []
        engine.can_export.return_value = True

        recommendation_engine = (
            recommendation_cls.return_value
        )

        recommendation_engine.recommend.return_value = []

        CanonicalManufacturingExportService.export(
            None,
            "dummy.csv"
        )

        recommendation_engine.recommend.assert_called_once()


if __name__ == "__main__":
    unittest.main()
