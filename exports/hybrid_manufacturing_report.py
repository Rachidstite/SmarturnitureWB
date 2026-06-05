from dataclasses import dataclass, field
from typing import List

from manufacturing.hybrid_extractor import \
    HybridManufacturingExtractor


@dataclass
class HybridManufacturingLine:
    part_id: str
    operation_type: str
    diameter: float
    depth: float
    source: str


@dataclass
class HybridManufacturingReport:
    lines: List[HybridManufacturingLine] = field(
        default_factory=list
    )


class HybridManufacturingReportEngine:

    @staticmethod
    def generate(scene_graph):

        specs = (
            HybridManufacturingExtractor
            .extract(scene_graph)
        )

        report = HybridManufacturingReport()

        for spec in specs:

            for op in getattr(
                spec,
                "unified_operations",
                []
            ):

                report.lines.append(
                    HybridManufacturingLine(
                        part_id=spec.identity,
                        operation_type=op.operation_type,
                        diameter=op.diameter,
                        depth=op.depth,
                        source=op.source
                    )
                )

        return report
