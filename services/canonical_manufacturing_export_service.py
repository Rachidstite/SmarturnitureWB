from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from exports.canonical_cnc_exporter import (
    CanonicalCNCExporter,
)

from exports.canonical_csv_exporter import (
    CanonicalCSVExporter,
)

from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)



class CanonicalManufacturingExportService:

    @staticmethod
    def export(scene_graph, filepath):

        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        validation_results = (
            ManufacturingRuleEngine()
            .validate(panel_specs)
        )

        if not (
            ManufacturingRuleEngine()
            .can_export(
                validation_results
            )
        ):
            raise RuntimeError(
                "Manufacturing intelligence validation failed"
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
