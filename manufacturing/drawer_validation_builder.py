from manufacturing.drawer_validation_report import DrawerValidationReport


WIDE_DRAWER_THRESHOLD = 800.0
DEEP_DRAWER_THRESHOLD = 550.0
MIN_BOTTOM_PANEL_THICKNESS = 6.0


class DrawerValidationBuilder:

    def build(self, drawer_rules_report):
        drawer_width = getattr(drawer_rules_report, "drawer_width", 0.0)
        drawer_depth = getattr(drawer_rules_report, "drawer_depth", 0.0)
        slide_length = getattr(drawer_rules_report, "slide_length", 0.0)
        bottom_panel_thickness = getattr(
            drawer_rules_report,
            "bottom_panel_thickness",
            0.0,
        )
        hardware_complete = bool(getattr(drawer_rules_report, "hardware_complete", False))

        if drawer_width <= 0:
            drawer_width_risk = "HIGH"
        elif drawer_width >= WIDE_DRAWER_THRESHOLD:
            drawer_width_risk = "MEDIUM"
        else:
            drawer_width_risk = "LOW"

        if drawer_depth <= 0:
            drawer_depth_risk = "HIGH"
        elif drawer_depth >= DEEP_DRAWER_THRESHOLD:
            drawer_depth_risk = "MEDIUM"
        else:
            drawer_depth_risk = "LOW"

        if 0 < bottom_panel_thickness < MIN_BOTTOM_PANEL_THICKNESS:
            bottom_panel_warning = "Drawer bottom panel may be too thin"
        else:
            bottom_panel_warning = ""

        if slide_length <= 0:
            slide_installation_valid = False
        elif drawer_depth > 0 and slide_length > drawer_depth:
            slide_installation_valid = False
        else:
            slide_installation_valid = True

        clearance_valid = not (drawer_width <= 0 or drawer_depth <= 0)

        blocking_issues = []
        if drawer_width_risk == "HIGH":
            blocking_issues.append("Drawer width must be greater than zero")
        if drawer_depth_risk == "HIGH":
            blocking_issues.append("Drawer depth must be greater than zero")
        if not slide_installation_valid:
            blocking_issues.append("Drawer slide installation is invalid")
        if not hardware_complete:
            blocking_issues.append("Drawer hardware is incomplete")

        warnings = []
        if drawer_width_risk == "MEDIUM":
            warnings.append("Wide drawer requires review")
        if drawer_depth_risk == "MEDIUM":
            warnings.append("Deep drawer requires review")
        if bottom_panel_warning:
            warnings.append(bottom_panel_warning)

        is_valid = not (
            drawer_width_risk == "HIGH"
            or drawer_depth_risk == "HIGH"
            or slide_installation_valid is False
            or clearance_valid is False
            or hardware_complete is False
        )

        manufacturing_ready = (
            is_valid
            and drawer_width_risk != "MEDIUM"
            and drawer_depth_risk != "MEDIUM"
            and bottom_panel_warning == ""
        )

        requires_review = (
            drawer_width_risk == "MEDIUM"
            or drawer_depth_risk == "MEDIUM"
            or bottom_panel_warning != ""
        )

        report = DrawerValidationReport(
            is_valid=is_valid,
            manufacturing_ready=manufacturing_ready,
            slide_installation_valid=slide_installation_valid,
            clearance_valid=clearance_valid,
            hardware_complete=hardware_complete,
            blocking_issues=blocking_issues,
            warnings=warnings,
        )
        report.drawer_width_risk = drawer_width_risk
        report.drawer_depth_risk = drawer_depth_risk
        report.bottom_panel_warning = bottom_panel_warning
        report.requires_review = requires_review
        return report
