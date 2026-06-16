from math import ceil

from manufacturing.sheet_utilization_report import SheetUtilizationReport


class SheetUtilizationBuilder:
    _STANDARD_SHEET_AREA_M2 = 5.796

    def build(self, metrics_report):
        total_panel_area_m2 = metrics_report.total_panel_area_m2
        warnings = list(metrics_report.warnings)

        if total_panel_area_m2 == 0:
            return SheetUtilizationReport(warnings=warnings)

        required_sheets = ceil(
            total_panel_area_m2 / self._STANDARD_SHEET_AREA_M2
        )
        total_sheet_area_m2 = required_sheets * self._STANDARD_SHEET_AREA_M2
        used_area_m2 = total_panel_area_m2
        waste_area_m2 = total_sheet_area_m2 - used_area_m2
        utilization_percent = (used_area_m2 / total_sheet_area_m2) * 100
        waste_percent = (waste_area_m2 / total_sheet_area_m2) * 100

        return SheetUtilizationReport(
            total_sheet_area_m2=total_sheet_area_m2,
            used_area_m2=used_area_m2,
            waste_area_m2=waste_area_m2,
            utilization_percent=utilization_percent,
            waste_percent=waste_percent,
            warnings=warnings,
        )
