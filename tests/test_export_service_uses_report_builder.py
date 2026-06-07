import unittest
from unittest.mock import patch

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportServiceUsesReportBuilder(
    unittest.TestCase
):

    @patch(
        "services.canonical_manufacturing_export_service.CanonicalCSVExporter.export"
    )
    @patch(
        "services.canonical_manufacturing_export_service.CanonicalCNCExporter.export_rows"
    )
    @patch(
        "services.canonical_manufacturing_export_service.ManufacturingIntelligenceReportBuilder"
    )
    @patch(
        "services.canonical_manufacturing_export_service.HybridManufacturingExtractor"
    )
    def test_service_uses_report_builder(
        self,
        extractor,
        builder_cls,
        exporter,
        csv_exporter
    ):

        extractor.extract.return_value = []

        report = (
            builder_cls.return_value.build.return_value
        )

        report.can_export = True

        CanonicalManufacturingExportService.export(
            None,
            "dummy.csv"
        )

        builder_cls.return_value.build.assert_called_once()


if __name__ == "__main__":
    unittest.main()
