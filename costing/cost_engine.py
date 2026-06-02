from dataclasses import dataclass
from exports.bom_engine import BOMReport

MDF_SHEET_AREA = 2.8 * 2.1
MDF_SHEET_PRICE = 800.0

BACK_SHEET_AREA = 2.8 * 2.1
BACK_SHEET_PRICE = 300.0

PVC_PRICE_PER_METER = 5.0

@dataclass
class CostReport:
    mdf_sheets: float = 0
    mdf_cost: float = 0

    back_sheets: float = 0
    back_cost: float = 0

    pvc_meters: float = 0
    pvc_cost: float = 0

    material_cost: float = 0

    labor_cost: float = 0
    overhead_cost: float = 0

    total_cost: float = 0
    selling_price: float = 0
    profit: float = 0


class CostEngine:

    @staticmethod
    def generate(
        bom: BOMReport,
        labor_cost: float = 500,
        overhead_cost: float = 200,
        profit_margin: float = 0.30
    ):

        report = CostReport()

        mdf_area = 0.0
        back_area = 0.0

        for item in bom.items:

            area = (
                item.width *
                item.height *
                item.quantity
            ) / 1000000

            material = item.material.upper()

            if "HDF" in material or "BACK" in material:
                back_area += area
            else:
                mdf_area += area

        report.mdf_sheets = mdf_area / MDF_SHEET_AREA
        report.mdf_cost = report.mdf_sheets * MDF_SHEET_PRICE

        report.back_sheets = back_area / BACK_SHEET_AREA
        report.back_cost = report.back_sheets * BACK_SHEET_PRICE

        report.pvc_meters = bom.edge_band_report.total_linear_meters
        report.pvc_cost = report.pvc_meters * PVC_PRICE_PER_METER

        report.material_cost = (
            report.mdf_cost +
            report.back_cost +
            report.pvc_cost
        )

        report.labor_cost = labor_cost
        report.overhead_cost = overhead_cost

        report.total_cost = (
            report.material_cost +
            report.labor_cost +
            report.overhead_cost
        )

        report.selling_price = (
            report.total_cost *
            (1 + profit_margin)
        )

        report.profit = (
            report.selling_price -
            report.total_cost
        )

        return report
