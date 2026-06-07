import unittest
from unittest.mock import patch

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportServiceGeneratesIntelligenceReport(
    unittest.TestCase
):

    @patch(
        "services.canonical_manufacturing_export_service.ManufacturingIntelligenceCSVReport"
    )
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
        "services.canonical_manufacturing_export_service.HybridManufacturingExtractor.extract"
    )
    def test_intelligence_report_is_generated(
        self,
        extract,
        builder_cls,
        cnc_export,
        csv_export,
        report_cls
    ):

        extract.return_value = []

        report = builder_cls.return_value.build.return_value
        report.can_export = True

        CanonicalManufacturingExportService.export(
            object(),
            "dummy.csv"
        )

        report_cls.return_value.build.assert_called_once()


if __name__ == "__main__":
    unittest.main()
