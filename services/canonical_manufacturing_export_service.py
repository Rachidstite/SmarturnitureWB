from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from exports.canonical_cnc_exporter import (
    CanonicalCNCExporter,
)

from exports.canonical_csv_exporter import (
    CanonicalCSVExporter,
)

from exports.manufacturing_intelligence_csv_exporter import (
    ManufacturingIntelligenceCSVExporter,
)

from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)

from validation.intelligence.manufacturing_intelligence_csv_report import (
    ManufacturingIntelligenceCSVReport,
)


class CanonicalManufacturingExportService:

    @staticmethod
    def export(scene_graph, filepath):

        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build(panel_specs)
        )

        if not report.can_export:
            raise RuntimeError(
                "Manufacturing intelligence validation failed"
            )

        intelligence_rows = (
            ManufacturingIntelligenceCSVReport()
            .build(report)
        )

        ManufacturingIntelligenceCSVExporter().export(
            intelligence_rows,
            filepath + ".intelligence.csv"
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
