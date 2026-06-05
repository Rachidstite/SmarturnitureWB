from manufacturing.extractor import \
    ManufacturingExtractor

from manufacturing.unified_operation_collector import \
    UnifiedOperationCollector


class HybridManufacturingExtractor:

    @staticmethod
    def extract(scene_graph):

        specs = (
            ManufacturingExtractor.extract(
                scene_graph
            )
        )

        unified_ops = (
            UnifiedOperationCollector
            .collect_hybrid(scene_graph)
        )

        for spec in specs:
            spec.unified_operations = list(
                unified_ops
            )

        return specs
