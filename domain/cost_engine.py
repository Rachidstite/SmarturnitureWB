from dataclasses import dataclass
import math

@dataclass
class CostReport:
    mdf_sheets: float
    mdf_cost: float
    back_cost: float
    total_cost: float

class CostEngine:

    MDF_SHEET_AREA = 2.80 * 2.10
    MDF_SHEET_PRICE = 800

    BACK_PANEL_PRICE = 300

    @classmethod
    def calculate(cls, total_panel_area_m2: float, back_count: int = 1):

        sheets = math.ceil(total_panel_area_m2 / cls.MDF_SHEET_AREA)

        mdf_cost = sheets * cls.MDF_SHEET_PRICE

        back_cost = back_count * cls.BACK_PANEL_PRICE

        return CostReport(
            mdf_sheets=sheets,
            mdf_cost=mdf_cost,
            back_cost=back_cost,
            total_cost=mdf_cost + back_cost
        )

    @classmethod
    def from_bom(cls, report):

        sheets = math.ceil(
            report.total_area_m2 / cls.MDF_SHEET_AREA
        )

        mdf_cost = sheets * cls.MDF_SHEET_PRICE

        back_count = 0

        for item in report.items:
            if (
                "BACK" in item.role.upper()
                or item.thickness <= 6
            ):
                back_count += item.quantity

        back_cost = back_count * cls.BACK_PANEL_PRICE

        return CostReport(
            mdf_sheets=sheets,
            mdf_cost=mdf_cost,
            back_cost=back_cost,
            total_cost=mdf_cost + back_cost
        )



