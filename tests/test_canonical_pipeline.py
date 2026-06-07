import os
import tempfile
import unittest

from domain.builders import WardrobeBuilder

from domain.rules_engine import (
    RuleContext,
    HardwarePlacementEngine,
)

from domain.manufacturing_compiler import (
    ManufacturingCompiler,
)

from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from exports.canonical_cnc_exporter import (
    CanonicalCNCExporter,
)

from exports.canonical_csv_exporter import (
    CanonicalCSVExporter,
)


class TestCanonicalPipeline(unittest.TestCase):

    def test_pipeline_exports_csv(self):

        project = (
            WardrobeBuilder(
                uid="PIPELINE",
                width=800,
                height=800,
                depth=400,
            ).build()
        )

        context = RuleContext()

        HardwarePlacementEngine(
            context
        ).process(project)

        ManufacturingCompiler().compile(
            project,
            context
        )

        specs = (
            HybridManufacturingExtractor
            .extract(project.graph)
        )

        rows = (
            CanonicalCNCExporter
            .export_rows(specs)
        )

        self.assertGreater(len(rows), 0)

        with tempfile.TemporaryDirectory() as tmp:

            path = os.path.join(
                tmp,
                "manufacturing.csv"
            )

            CanonicalCSVExporter.export(
                rows,
                path
            )

            self.assertTrue(
                os.path.exists(path)
            )


if __name__ == "__main__":
    unittest.main()
