import os
import tempfile
import unittest

from domain.builders import WardrobeBuilder
from domain.rules_engine import (
    HardwarePlacementEngine,
    RuleContext,
)
from domain.manufacturing_compiler import (
    ManufacturingCompiler,
)

from exports.cnc_exporter import CNCExporter

from services.canonical_manufacturing_export_service import (
    CanonicalManufacturingExportService,
)


class TestExportParity(unittest.TestCase):

    def test_both_exporters_generate_files(self):

        cabinet = WardrobeBuilder(
            uid="PARITY",
            width=800,
            height=800,
            depth=400,
        )

        project = cabinet.build()

        context = RuleContext()

        HardwarePlacementEngine(
            context
        ).process(project)

        ManufacturingCompiler().compile(
            project,
            context
        )

        with tempfile.TemporaryDirectory() as tmp:

            legacy_csv = os.path.join(
                tmp,
                "legacy.csv"
            )

            canonical_csv = os.path.join(
                tmp,
                "canonical.csv"
            )

            CNCExporter.export_master_drilling_map(
                project,
                legacy_csv
            )

            CanonicalManufacturingExportService.export(
                project.graph,
                canonical_csv
            )

            self.assertTrue(
                os.path.exists(legacy_csv)
            )

            self.assertTrue(
                os.path.exists(canonical_csv)
            )


if __name__ == "__main__":
    unittest.main()
