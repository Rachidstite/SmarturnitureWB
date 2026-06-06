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

            enriched_ops = []

            for op in unified_ops:

                owner = (
                    op.metadata.get("panel_id")
                )

                if (
                    owner is not None
                    and owner != spec.identity
                ):
                    continue

                metadata = dict(op.metadata)

                metadata.update({
                    "panel_id": spec.identity,
                    "panel_role": str(spec.role),
                    "panel_thickness": spec.thickness,
                })

                enriched_ops.append(
                    op.__class__(
                        operation_type=op.operation_type,
                        diameter=op.diameter,
                        depth=op.depth,
                        x=op.x,
                        y=op.y,
                        z=op.z,
                        face=op.face,
                        axis=op.axis,
                        source=op.source,
                        metadata=metadata,
                    )
                )

            spec.unified_operations = enriched_ops

        return specs
