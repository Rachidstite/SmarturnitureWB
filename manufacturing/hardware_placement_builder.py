from manufacturing.hardware_placement_report import HardwarePlacementReport


class HardwarePlacementBuilder:

    def build(self, minifix_report=None, confirmat_report=None, hinge_report=None):
        reports = [minifix_report, confirmat_report, hinge_report]
        present_reports = [report for report in reports if report is not None]

        if not present_reports:
            hardware_risk = "HIGH"
        elif any(not getattr(report, "is_valid", True) for report in present_reports):
            hardware_risk = "HIGH"
        elif any(self._requires_review(report) for report in present_reports):
            hardware_risk = "MEDIUM"
        else:
            hardware_risk = "LOW"

        if hardware_risk == "HIGH":
            hardware_recommendation = "Hardware engineering review required"
        elif hardware_risk == "MEDIUM":
            hardware_recommendation = "Hardware placement review recommended"
        else:
            hardware_recommendation = ""

        placement_quality = "UNKNOWN"
        fastener_coverage = "UNKNOWN"
        if hardware_risk == "LOW":
            placement_quality = "GOOD"
            fastener_coverage = "GOOD"
        elif hardware_risk == "MEDIUM":
            placement_quality = "REVIEW"
            fastener_coverage = "REVIEW"
        else:
            placement_quality = "POOR"
            fastener_coverage = "POOR"

        return HardwarePlacementReport(
            placement_quality=placement_quality,
            fastener_coverage=fastener_coverage,
            hardware_risk=hardware_risk,
            hardware_recommendation=hardware_recommendation,
        )

    @staticmethod
    def _requires_review(report):
        if getattr(report, "requires_review", False):
            return True
        if getattr(report, "manufacturing_warning", ""):
            return True
        if getattr(report, "recommended_action", ""):
            return True
        if getattr(report, "hinge_requirement", "") in {"MEDIUM", "HIGH"}:
            return True
        if getattr(report, "door_recommendation", ""):
            return True
        return False
