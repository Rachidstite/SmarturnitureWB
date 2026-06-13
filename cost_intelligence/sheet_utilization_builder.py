from cost_intelligence.sheet_utilization_report import SheetUtilizationReport


class SheetUtilizationBuilder:

    def build(self, sheet_results):
        warnings = []
        if not sheet_results:
            warnings.append("No sheet results available")

        has_missing_dimensions = any(
            not getattr(sheet, "sheet_width", 0)
            or not getattr(sheet, "sheet_height", 0)
            for sheet in sheet_results
        )
        if has_missing_dimensions:
            warnings.append("Sheet result has missing or zero dimensions")

        total_sheet_area = sum(
            getattr(sheet, "sheet_width", 0)
            * getattr(sheet, "sheet_height", 0)
            for sheet in sheet_results
        )
        total_used_area = sum(sheet.used_area for sheet in sheet_results)
        total_remaining_area = total_sheet_area - total_used_area

        if total_sheet_area > 0:
            utilization_rate = total_used_area / total_sheet_area
            waste_rate = 1 - utilization_rate
        else:
            utilization_rate = 0.0
            waste_rate = 0.0

        return SheetUtilizationReport(
            sheet_count=len(sheet_results),
            total_sheet_area=total_sheet_area,
            total_used_area=total_used_area,
            total_remaining_area=total_remaining_area,
            utilization_rate=utilization_rate,
            waste_rate=waste_rate,
            warnings=warnings,
        )
