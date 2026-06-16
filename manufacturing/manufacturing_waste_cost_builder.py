from manufacturing.manufacturing_waste_cost_report import (
    ManufacturingWasteCostReport,
)


class ManufacturingWasteCostBuilder:
    _STANDARD_SHEET_AREA_M2 = 5.796
    _SHEET_COST = 800.0

    def build(self, sheet_utilization_report):
        waste_area_m2 = sheet_utilization_report.waste_area_m2
        warnings = list(sheet_utilization_report.warnings)
        cost_per_m2 = self._SHEET_COST / self._STANDARD_SHEET_AREA_M2
        estimated_waste_cost = waste_area_m2 * cost_per_m2

        return ManufacturingWasteCostReport(
            waste_area_m2=waste_area_m2,
            estimated_waste_cost=estimated_waste_cost,
            sheet_cost=self._SHEET_COST,
            warnings=warnings,
        )
