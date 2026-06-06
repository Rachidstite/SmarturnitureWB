import inspect
import unittest

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestCanonicalExportServiceArchitecture(
    unittest.TestCase
):

    def test_export_service_has_no_legacy_dependencies(self):

        source = inspect.getsource(
            CanonicalManufacturingExportService
        )

        self.assertNotIn(
            "collect_legacy",
            source
        )

        self.assertNotIn(
            "collect_hybrid",
            source
        )

        self.assertNotIn(
            "LegacyOperationAdapter",
            source
        )

        self.assertNotIn(
            "PanelOperationEngine",
            source
        )


if __name__ == "__main__":
    unittest.main()
