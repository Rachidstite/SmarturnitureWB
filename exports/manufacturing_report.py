from dataclasses import dataclass, field
from typing import List

from manufacturing.extractor import ManufacturingExtractor


@dataclass
class ManufacturingLine:
    part_id: str
    operation: str


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

                report.lines.append(
                    ManufacturingLine(
                        part_id=spec.identity,
                        operation=str(op)
                    )
                )

        return report

    @staticmethod
    def export_csv(report, filepath):

        import csv

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:

            w = csv.writer(f)

            w.writerow([
                "Part",
                "Operation"
            ])

            for line in report.lines:
                w.writerow([
                    line.part_id,
                    line.operation
                ])

        print(f"Manufacturing report exported to {filepath}")
