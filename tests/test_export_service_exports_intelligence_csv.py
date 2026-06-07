import unittest
from unittest.mock import patch

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportServiceExportsIntelligenceCSV(
    unittest.TestCase
):

    @patch(
        "services.canonical_manufacturing_export_service.ManufacturingIntelligenceCSVExporter"
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
    def test_exports_intelligence_csv(
        self,
        extract,
        builder_cls,
        cnc_export,
        csv_export,
        intelligence_exporter_cls
    ):

        extract.return_value = []

        report = builder_cls.return_value.build.return_value
        report.can_export = True

        CanonicalManufacturingExportService.export(
            object(),
            "dummy.csv"
        )

        intelligence_exporter_cls.return_value.export.assert_called_once()


if __name__ == "__main__":
    unittest.main()
