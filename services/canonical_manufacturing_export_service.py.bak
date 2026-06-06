from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from exports.canonical_cnc_exporter import (
    CanonicalCNCExporter,
)

from exports.canonical_csv_exporter import (
    CanonicalCSVExporter,
)


class CanonicalManufacturingExportService:

    @staticmethod
    def export(scene_graph, filepath):

        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        rows = (
            CanonicalCNCExporter.export_rows(
                panel_specs
            )
        )

        return (
            CanonicalCSVExporter.export(
                rows,
                filepath
            )
        )
