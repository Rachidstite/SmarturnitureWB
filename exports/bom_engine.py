from dataclasses import dataclass, field
from typing import List, Dict
from manufacturing.panel_spec import PanelSpec
from manufacturing.extractor import ManufacturingExtractor
from manufacturing.edge_spec import EdgeSpec

@dataclass
class BOMItem:
    identity: str
    role: str
    width: float
    height: float
    thickness: float
    material: str
    group: str
    edge_top: str = ""
    edge_bottom: str = ""
    edge_left: str = ""
    edge_right: str = ""
    quantity: int = 1

@dataclass
class EdgeBandReport:
    """تقرير منفصل لشريط اللصق."""
    total_linear_meters: float = 0.0
    by_type: Dict[str, float] = field(default_factory=dict)  # "ABS_1MM" → متر طولي
    details: List[str] = field(default_factory=list)

@dataclass
class BOMReport:
    items: List[BOMItem] = field(default_factory=list)
    total_panels: int = 0
    total_area_m2: float = 0.0
    material_summary: Dict[str, int] = field(default_factory=dict)
    edge_band_report: EdgeBandReport = field(default_factory=EdgeBandReport)

class BOMEngine:
    @staticmethod
    def generate(scene_graph) -> BOMReport:
        specs = ManufacturingExtractor.extract(scene_graph)
        report = BOMReport()

        for spec in specs:
            edges = spec.edge_spec if spec.edge_spec else EdgeSpec()
            item = BOMItem(
                identity=spec.identity,
                role=spec.role.name if hasattr(spec.role, 'name') else str(spec.role),
                width=spec.width, height=spec.height, thickness=spec.thickness,
                material=spec.material, group=spec.group,
                edge_top=edges.top or "",
                edge_bottom=edges.bottom or "",
                edge_left=edges.left or "",
                edge_right=edges.right or "",
                quantity=spec.quantity
            )
            report.items.append(item)

            # تجميع الأمتار الطولية
            lm = edges.linear_meters(spec.width, spec.height)
            if lm > 0:
                report.edge_band_report.total_linear_meters += lm
                for edge_name, edge_type in edges.all_banded().items():
                    report.edge_band_report.by_type[edge_type] =                         report.edge_band_report.by_type.get(edge_type, 0.0) + lm
                report.edge_band_report.details.append(
                    f"{spec.identity}: {edges.all_banded()} ({lm:.3f}m)"
                )

        report.total_panels = len(report.items)
        report.total_area_m2 = sum(
            (item.width * item.height) / 1_000_000 for item in report.items
        )
        for item in report.items:
            mat = item.material
            report.material_summary[mat] = report.material_summary.get(mat, 0) + 1

        return report

    @staticmethod
    def export_csv(report: BOMReport, filepath: str):
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # رأس الأعمدة
            writer.writerow(["Part ID", "Role", "Width", "Height", "Thickness", "Material",
                             "Group", "Edge T", "Edge B", "Edge L", "Edge R", "Qty"])
            for item in report.items:
                writer.writerow([
                    item.identity, item.role,
                    round(item.width,1), round(item.height,1), round(item.thickness,1),
                    item.material, item.group,
                    item.edge_top, item.edge_bottom, item.edge_left, item.edge_right,
                    item.quantity
                ])
            # ملخص
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Panels", report.total_panels])
            writer.writerow(["Total Area (m²)", round(report.total_area_m2, 4)])
            # ملخص الخامات
            writer.writerow([])
            writer.writerow(["MATERIAL SUMMARY"])
            for mat, count in report.material_summary.items():
                writer.writerow([mat, count])
            # تقرير الحواف
            if report.edge_band_report.total_linear_meters > 0:
                writer.writerow([])
                writer.writerow(["EDGE BAND SUMMARY"])
                writer.writerow(["Total Linear Meters", round(report.edge_band_report.total_linear_meters, 3)])
                for etype, lm in report.edge_band_report.by_type.items():
                    writer.writerow([f"  {etype}", f"{lm:.3f} m"])
                writer.writerow([])
                writer.writerow(["EDGE BAND DETAILS"])
                for detail in report.edge_band_report.details:
                    writer.writerow([detail])
        print(f"BOM exported to {filepath}")
