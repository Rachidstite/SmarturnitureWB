import unittest
from unittest.mock import patch

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportServiceBlocking(
    unittest.TestCase
):

    @patch(
        "services.canonical_manufacturing_export_service.HybridManufacturingExtractor"
    )
    @patch(
        "services.canonical_manufacturing_export_service.ManufacturingIntelligenceReportBuilder"
    )
    def test_export_blocked_when_errors_exist(
        self,
        builder_cls,
        extractor_cls
    ):

        extractor_cls.extract.return_value = []

        report = (
            builder_cls.return_value.build.return_value
        )

        report.can_export = False

        with self.assertRaises(
            RuntimeError
        ):
            CanonicalManufacturingExportService.export(
                object(),
                "dummy.csv"
            )


if __name__ == "__main__":
    unittest.main()
