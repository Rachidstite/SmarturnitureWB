from dataclasses import dataclass, field
from typing import List

from manufacturing.extractor import ManufacturingExtractor


@dataclass
class ManufacturingLine:
    part_id: str
    operation_type: str
    diameter: float
    depth: float
    face_or_edge: str
    description: str


@dataclass
class ManufacturingReport:
    lines: List[ManufacturingLine] = field(default_factory=list)


class ManufacturingReportEngine:

    @staticmethod
    def generate(scene_graph):

        specs = ManufacturingExtractor.extract(scene_graph)

        report = ManufacturingReport()

        for spec in specs:

            for op in spec.cnc_operations:

                operation_type = type(op).__name__

                diameter = getattr(op, "diameter", 0)
                depth = getattr(op, "depth", 0)

                face_or_edge = ""

                if hasattr(op, "face"):
                    face_or_edge = op.face

                if hasattr(op, "edge"):
                    face_or_edge = op.edge

                report.lines.append(
                    ManufacturingLine(
                        part_id=spec.identity,
                        operation_type=operation_type,
                        diameter=diameter,
                        depth=depth,
                        face_or_edge=face_or_edge,
                        description=str(op)
                    )
                )

        return report

    @staticmethod
    def export_csv(report, filepath):

        import csv

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:

            w = csv.writer(f)

            w.writerow([
                "Part ID",
                "Operation",
                "Diameter",
                "Depth",
                "Face/Edge",
                "Description"
            ])

            for line in report.lines:

                w.writerow([
                    line.part_id,
                    line.operation_type,
                    line.diameter,
                    line.depth,
                    line.face_or_edge,
                    line.description
                ])

        print(
            f"Manufacturing report exported to {filepath}"
        )
