from manufacturing.back_panel_validation_report import BackPanelValidationReport


WIDE_PANEL_THRESHOLD = 800.0
TALL_PANEL_THRESHOLD = 1800.0
MAX_SAFE_SPACING = 300.0


class BackPanelValidationBuilder:

    def build(
        self,
        hole_rules_report,
        manufacturing_intent_report,
        hole_placement_report=None,
        hole_pattern_report=None,
        *,
        geometry_report=None,
    ):
        minimum_panel_width = getattr(hole_rules_report, "minimum_panel_width", 0.0)
        minimum_panel_height = getattr(
            hole_rules_report,
            "minimum_panel_height",
            0.0,
        )
        maximum_spacing = getattr(hole_rules_report, "maximum_spacing", 0.0)

        if minimum_panel_width <= 0:
            width_risk = "HIGH"
        elif minimum_panel_width >= WIDE_PANEL_THRESHOLD:
            width_risk = "MEDIUM"
        else:
            width_risk = "LOW"

        if minimum_panel_height <= 0:
            height_risk = "HIGH"
        elif minimum_panel_height >= TALL_PANEL_THRESHOLD:
            height_risk = "MEDIUM"
        else:
            height_risk = "LOW"

        if maximum_spacing <= 0:
            spacing_risk = "HIGH"
        elif maximum_spacing > MAX_SAFE_SPACING:
            spacing_risk = "MEDIUM"
        else:
            spacing_risk = "LOW"

        edge_risk = "LOW"
        corner_risk = "LOW"

        center_holes_required = getattr(
            hole_rules_report,
            "requires_center_holes",
            False,
        )
        base_center_support_required = getattr(
            manufacturing_intent_report,
            "requires_center_support",
            False,
        )
        center_support_required = (
            base_center_support_required
            or width_risk == "MEDIUM"
            or height_risk == "MEDIUM"
        )
        if geometry_report is not None:
            center_support_required = (
                center_support_required
                or getattr(geometry_report, "width", 0.0) >= WIDE_PANEL_THRESHOLD
                or getattr(geometry_report, "height", 0.0) >= TALL_PANEL_THRESHOLD
            )

        fixing_method_warning = ""
        if (
            getattr(manufacturing_intent_report, "requires_groove", False) is False
            and getattr(manufacturing_intent_report, "requires_fasteners", False)
            is False
        ):
            fixing_method_warning = "Back panel has no fixing method"

        manufacturing_warning = ""
        if width_risk == "MEDIUM":
            manufacturing_warning = "Wide back panel requires structural review"
        elif height_risk == "MEDIUM":
            manufacturing_warning = "Tall back panel requires structural review"
        elif spacing_risk == "MEDIUM":
            manufacturing_warning = "Back panel fixing spacing requires review"
        elif getattr(
            manufacturing_intent_report,
            "visual_manufacturing_intent_required",
            False,
        ):
            manufacturing_warning = (
                "Back panel requires visual manufacturing intent review"
            )

        hole_valid = True
        hole_spacing_warning = ""
        hole_count_consistency_warning = ""
        hole_edge_warning = ""
        hole_pattern_warning = ""
        hole_count_warning = ""
        hole_center_warning = ""
        hole_support_warning = ""

        if hole_placement_report is not None or hole_pattern_report is not None:
            hole_valid, hole_count_warning, hole_center_warning = (
                self._validate_hole_count_and_center(
                    hole_rules_report,
                    hole_pattern_report,
                    manufacturing_intent_report,
                )
            )
            hole_spacing_warning = self._validate_hole_spacing(
                hole_rules_report,
                hole_placement_report,
            )
            hole_count_consistency_warning = (
                self._validate_hole_position_count_consistency(
                    hole_placement_report,
                    hole_pattern_report,
                )
            )
            hole_edge_warning = self._validate_hole_edges(hole_pattern_report)
            hole_pattern_warning = self._validate_pattern_suitability(
                hole_pattern_report,
                manufacturing_intent_report,
            )
            hole_support_warning, hole_support_valid = self._validate_support_capability(
                hole_placement_report,
                manufacturing_intent_report,
            )
            hole_valid = hole_valid and hole_support_valid

        manufacturing_warning = self._join_warnings(
            manufacturing_warning,
            hole_spacing_warning,
            hole_count_consistency_warning,
            hole_edge_warning,
            hole_pattern_warning,
            hole_count_warning,
            hole_center_warning,
        )
        fixing_method_warning = self._join_warnings(
            fixing_method_warning,
            hole_support_warning,
        )

        is_valid = not any(
            risk == "HIGH"
            for risk in (width_risk, height_risk, spacing_risk, edge_risk, corner_risk)
        )
        if hole_placement_report is not None or hole_pattern_report is not None:
            is_valid = is_valid and hole_valid
        if not is_valid:
            validation_status = "BLOCKED"
            recommended_action = (
                manufacturing_warning
                or fixing_method_warning
                or "Review back panel manufacturing rules"
            )
        elif width_risk == "MEDIUM" or height_risk == "MEDIUM" or spacing_risk == "MEDIUM":
            validation_status = "VALID_WITH_WARNINGS"
            recommended_action = "Review back panel engineering rules"
        elif fixing_method_warning:
            validation_status = "VALID_WITH_WARNINGS"
            recommended_action = "Review back panel engineering rules"
        elif manufacturing_warning:
            validation_status = "VALID_WITH_WARNINGS"
            recommended_action = "Review back panel manufacturing intent"
        else:
            validation_status = "VALID"
            recommended_action = ""

        return BackPanelValidationReport(
            is_valid=is_valid,
            validation_status=validation_status,
            width_risk=width_risk,
            height_risk=height_risk,
            spacing_risk=spacing_risk,
            edge_risk=edge_risk,
            corner_risk=corner_risk,
            center_support_required=center_support_required,
            center_holes_required=center_holes_required,
            fixing_method_warning=fixing_method_warning,
            manufacturing_warning=manufacturing_warning,
            recommended_action=recommended_action,
        )

    @staticmethod
    def _join_warnings(*warnings):
        return "; ".join(
            warning for warning in warnings if warning
        )

    @staticmethod
    def _validate_hole_spacing(hole_rules_report, hole_placement_report):
        if hole_placement_report is None:
            return ""

        maximum_spacing = getattr(hole_rules_report, "maximum_spacing", 0.0)
        coordinate_warning = (
            BackPanelValidationBuilder._validate_coordinate_hole_spacing(
                hole_placement_report,
                maximum_spacing,
            )
        )
        if coordinate_warning:
            return coordinate_warning

        default_spacing = getattr(hole_placement_report, "default_spacing", 0.0)
        if maximum_spacing > 0 and default_spacing > maximum_spacing:
            return "Back panel hole spacing exceeds maximum spacing"
        return ""

    @staticmethod
    def _validate_coordinate_hole_spacing(hole_placement_report, maximum_spacing):
        if maximum_spacing <= 0:
            return ""

        hole_positions = getattr(hole_placement_report, "hole_positions", None)
        if not hole_positions:
            return ""

        recognized_groups = {
            "TOP": ("x", []),
            "BOTTOM": ("x", []),
            "LEFT": ("y", []),
            "RIGHT": ("y", []),
        }

        for coordinate in hole_positions:
            face = str(getattr(coordinate, "face", "") or "").strip().upper()
            if face not in recognized_groups:
                continue

            axis_name, group = recognized_groups[face]
            axis_value = getattr(coordinate, axis_name, None)
            if not isinstance(axis_value, (int, float)):
                continue
            group.append(float(axis_value))

        for axis_name, values in recognized_groups.values():
            if len(values) < 2:
                continue

            ordered_values = sorted(values)
            for index in range(1, len(ordered_values)):
                if ordered_values[index] - ordered_values[index - 1] > maximum_spacing:
                    return "Back panel hole coordinate spacing exceeds maximum spacing"

        return ""

    @staticmethod
    def _validate_hole_position_count_consistency(
        hole_placement_report,
        hole_pattern_report,
    ):
        hole_positions = getattr(hole_placement_report, "hole_positions", None)
        if not hole_positions:
            return ""

        total_hole_count = getattr(hole_pattern_report, "total_hole_count", 0) or 0
        if total_hole_count <= 0:
            return ""

        if len(hole_positions) != total_hole_count:
            return "Back panel hole coordinate count does not match pattern count"
        return ""

    @staticmethod
    def _validate_hole_edges(hole_pattern_report):
        if hole_pattern_report is None:
            return ""

        total_hole_count = getattr(hole_pattern_report, "total_hole_count", 0) or 0
        if total_hole_count <= 0:
            return ""

        edge_counts = {
            "top": getattr(hole_pattern_report, "top_edge_holes", 0) or 0,
            "bottom": getattr(hole_pattern_report, "bottom_edge_holes", 0) or 0,
            "left": getattr(hole_pattern_report, "left_edge_holes", 0) or 0,
            "right": getattr(hole_pattern_report, "right_edge_holes", 0) or 0,
        }
        missing_edges = [
            edge_name for edge_name, count in edge_counts.items() if count <= 0
        ]
        if missing_edges:
            joined_edges = ", ".join(missing_edges)
            return f"Back panel hole edge coverage is incomplete: {joined_edges}"
        return ""

    @staticmethod
    def _validate_pattern_suitability(hole_pattern_report, manufacturing_intent_report):
        if hole_pattern_report is None:
            return ""

        pattern_type = str(getattr(hole_pattern_report, "pattern_type", "") or "")
        if not pattern_type:
            return "Back panel hole pattern suitability is unclear"

        pattern = pattern_type.upper()
        if (
            getattr(manufacturing_intent_report, "visual_manufacturing_intent_required", False)
            and pattern == "UNKNOWN"
        ):
            return "Back panel hole pattern requires visual manufacturing review"
        return ""

    @staticmethod
    def _validate_hole_count_and_center(
        hole_rules_report,
        hole_pattern_report,
        manufacturing_intent_report,
    ):
        requires_center_holes = getattr(
            hole_rules_report,
            "requires_center_holes",
            False,
        )
        if hole_pattern_report is None:
            return True, "", ""

        total_hole_count = getattr(hole_pattern_report, "total_hole_count", 0) or 0
        center_hole_count = getattr(hole_pattern_report, "center_hole_count", 0) or 0
        hole_count_warning = ""
        center_warning = ""
        valid = True

        hole_intelligence_relevant = getattr(
            manufacturing_intent_report,
            "requires_fasteners",
            False,
        )

        if hole_intelligence_relevant and total_hole_count <= 0:
            valid = False
            hole_count_warning = "Back panel hole count is insufficient"

        if requires_center_holes and center_hole_count <= 0:
            valid = False
            center_warning = "Back panel requires explicit center hole evidence"

        return valid, hole_count_warning, center_warning

    @staticmethod
    def _validate_support_capability(hole_placement_report, manufacturing_intent_report):
        if hole_placement_report is None:
            return "", True

        if BackPanelValidationBuilder._requires_screws(manufacturing_intent_report):
            if not getattr(hole_placement_report, "supports_screws", False):
                return "Back panel screw support is required but not supported", False

        if BackPanelValidationBuilder._requires_confirmat(manufacturing_intent_report):
            if not getattr(hole_placement_report, "supports_confirmat", False):
                return "Back panel confirmat support is required but not supported", False

        return "", True

    @staticmethod
    def _requires_screws(manufacturing_intent_report):
        fields = (
            getattr(manufacturing_intent_report, "fixing_intent", ""),
            getattr(manufacturing_intent_report, "manufacturing_intent", ""),
            getattr(manufacturing_intent_report, "back_panel_method", ""),
            getattr(manufacturing_intent_report, "fastener_type", ""),
        )
        return any("SCREW" in str(field).upper() for field in fields)

    @staticmethod
    def _requires_confirmat(manufacturing_intent_report):
        fields = (
            getattr(manufacturing_intent_report, "fixing_intent", ""),
            getattr(manufacturing_intent_report, "manufacturing_intent", ""),
            getattr(manufacturing_intent_report, "back_panel_method", ""),
            getattr(manufacturing_intent_report, "fastener_type", ""),
        )
        return any("CONFIRMAT" in str(field).upper() for field in fields)
