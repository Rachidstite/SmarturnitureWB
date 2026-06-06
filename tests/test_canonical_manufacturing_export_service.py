import os
import tempfile
import unittest

from domain.builders import WardrobeBuilder

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestCanonicalManufacturingExportService(
    unittest.TestCase
):

    def test_export_csv_file(self):

        project = (
            WardrobeBuilder(
                uid="EXPORT",
                width=800,
                height=800,
                depth=400,
            ).build()
        )

        with tempfile.TemporaryDirectory() as tmp:

            path = os.path.join(
                tmp,
                "manufacturing.csv"
            )

            result = (
                CanonicalManufacturingExportService
                .export(
                    project.graph,
                    path
                )
            )

            self.assertTrue(
                os.path.exists(result)
            )


if __name__ == "__main__":
    unittest.main()
