import os
import tempfile
import unittest

from domain.builders import WardrobeBuilder

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestCanonicalE2EPipeline(unittest.TestCase):

    def test_canonical_export_pipeline(self):

        project = (
            WardrobeBuilder(
                uid="CANONICAL_E2E",
                width=1000,
                height=2000,
                depth=600,
            ).build()
        )

        with tempfile.TemporaryDirectory() as tmp:

            csv_path = os.path.join(
                tmp,
                "canonical_manufacturing.csv"
            )

            result = (
                CanonicalManufacturingExportService
                .export(
                    project.graph,
                    csv_path
                )
            )

            self.assertTrue(
                os.path.exists(result)
            )

            with open(
                result,
                "r",
                encoding="utf-8"
            ) as f:

                lines = f.readlines()

            self.assertGreater(
                len(lines),
                1
            )


if __name__ == "__main__":
    unittest.main()
